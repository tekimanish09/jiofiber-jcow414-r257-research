# Technical Portfolio Case Study: Embedded Firmware Reverse Engineering & Security Analysis

**Project**: JioFiber Sercomm JCOW414 (Stock Firmware R2.57) to OpenWrt Conversion  
**Author / Researcher**: T. Manish ([GitHub: @tekimanish09](https://github.com/tekimanish09))  
**Domain**: Embedded Linux, Firmware Forensics, Applied Cryptography & Security Engineering  
**Target Hardware**: Sercomm JCOW414 (Airoha / Econet EN7528HU Dual-Core MIPS SoC)  

---

## Executive Overview & Engineering Competencies

This case study demonstrates end-to-end embedded systems reverse engineering, cryptographic analysis, and protocol security diagnostics on carrier-grade networking hardware. It serves as documented proof-of-work showcasing deep capabilities in:

* **Embedded Linux Internals**: MTD flash partitioning, U-Boot / Econet bootloaders, SquashFS root filesystems, and dual-bank bootflag toggling.
* **Applied Cryptography**: AES-128-CBC ciphertext analysis, OpenSSL salted binary format envelopes, key derivation message digests (SHA-256 vs legacy MD5), and mathematical reverse engineering of integrity checksum algorithms.
* **Vulnerability Analysis**: Embedded CGI parameter handling, Lua runtime execution vectors in configuration parsers, and daemon-level anti-rollback verification mechanics.
* **Network & Systems Diagnostics**: Socket probing, protocol tracing, cross-adapter network routing collisions, and client-side JavaScript execution anomalies.
* **Tool Authoring**: Production-grade verification tools in Python, shell interception loops, and automated cryptographic handlers.

---

## Comprehensive Engineering Log: Problems Faced, Root Cause Analysis & Solutions

The following section documents **every critical technical barrier** encountered during this investigation, providing complete transparency into the debugging methodology, root cause isolation, and engineering solutions.

```
+---------------------------------------------------------------------------------------------------------+
|                                    CHRONOLOGICAL CHALLENGE PIPELINE                                     |
+---------------------------------------------------------------------------------------------------------+
| [Problem 1: Anti-Rollback] -> [Problem 2: Checksum MD5] -> [Problem 3: OpenSSL Digests]               |
|                                                                                                         |
| [Problem 4: Web UI Freeze] -> [Problem 5: Unauth POSTs]  -> [Problem 6: Interface Gateway Collision]   |
+---------------------------------------------------------------------------------------------------------+
```

---

### Challenge 1: Stock R2.57 Firmware Downgrade Rejection
* **Symptom**: Attempting to upload stock `SRCMTF1_JCOW414_R2.15.img` with companion `SRCMTF1_JCOW414_R2.15.sig` via the vendor Web GUI triggered an immediate rejection:
  ```text
  Firmware file is invalid or corrupted.
  ```
* **Hypothesis Tested**:
  1. File corruption during download/transfer.
  2. Format mismatch or incorrect hardware target.
* **Diagnostic Methodology**:
  - Computed SHA-256 digests on local files and verified against community reference dumps:
    - `.img`: `ad2977cca4b2796faa81cf0bf7d6f16b152fffdef1c73aba6b6dabc725bbca97` (Match)
    - `.sig`: `669961ce8d04cd0e0d14181b49469f87143f190c89ec11f57bac88e14384ea91` (Match)
  - Inspected binary offsets: verified `HDR2` magic bytes at `0x000` and `0x100`, string `JCOW414_R2.15` at `0x110`, and version `2.15` at `0x01c`. Files were confirmed 100% structurally intact.
* **Root Cause**:
  Stock firmware R2.57 incorporates an internal validation binary that runs during upload. The binary enforces an **anti-rollback policy** (`target_version 2.15 < current_version 2.57`) and checks signature keys, logging the rejection code into `/tmp/firmCheckRes.txt`. The web interface checks this file and displays the generic "invalid or corrupted" message.
* **Engineering Solution**:
  Isolated the community bypass mechanism: running a high-frequency background shell loop that zeroes `/tmp/firmCheckRes.txt` (`cat /dev/null > /tmp/firmCheckRes.txt`) intercepts the error before the CGI handler evaluates it, tricking the firmware daemon into proceeding with the flash.
* **Key Takeaway**: A generic "corrupted file" UI error often masks an active security enforcement daemon in embedded systems. Verifying binary integrity via hashing prevents wasted time troubleshooting non-existent corruption.

---

### Challenge 2: Configuration Checksum Rejection during Restore
* **Symptom**: Injecting custom management commands into the decrypted router configuration caused the router to reject the restored configuration with checksum errors.
* **Diagnostic Methodology**:
  - Analyzed the decrypted configuration file (`~3,144` lines of Lua tables).
  - Identified declaration line 3012: `config.checksum = "7d669de3e42ace6be9ee2286398e46ca"`.
  - Tested multiple candidate hashing boundaries: entire file, specific tables, stripped newlines, and byte ranges.
* **Root Cause**:
  The router's configuration parser computes a standard **MD5** digest across all bytes from byte `0` up to immediately before the string `config.checksum = "`, including the trailing newline of line 3011 (`0x0A`). Modifying line 1 (adding `os.execute` payloads) altered the file's hash, causing a mismatch against the static declared checksum.
* **Engineering Solution**:
  Reverse-engineered the exact byte-level boundary and authored [`scripts/checksum_calculator.py`](../scripts/checksum_calculator.py). Verified that hashing byte 0 to 149,182 on the stock file produces `7d669de3e42ace6be9ee2286398e46ca` (100% match). Created `modified_correct.txt` with recalculation (`1cf7898852d9b5b9303be87bcd6aff4f`), achieving a fully validated, restore-ready configuration.
* **Key Takeaway**: Understanding exact parsing boundaries in embedded config parsers transforms an exploit attempt from an unverified shot in the dark into a mathematically sound, predictable process.

---

### Challenge 3: OpenSSL Modern vs Legacy Key Derivation (`-md sha256` vs `-md md5`)
* **Symptom**: Decrypting the factory `.enc` configuration backup using standard community scripts failed with:
  ```text
  bad decrypt
  error:1C800064:Provider routines:ossl_cipher_unpadblock:bad decrypt
  ```
* **Diagnostic Methodology**:
  - Examined the binary header of `.enc`: starts with ASCII `Salted__` followed by an 8-byte salt, confirming standard OpenSSL `EVP_BytesToKey` derivation.
  - Tested legacy OpenSSL 1.1 algorithms versus modern OpenSSL 3.x/4.x default algorithms.
* **Root Cause**:
  Legacy modding tutorials specified `openssl aes-128-cbc -d ... -md md5`. Modern OpenSSL installations and newer Sercomm firmwares use **SHA-256** as the message digest for deriving the key and IV from the passphrase. Using `-md md5` derived an incorrect AES key, leading to padding failure during block unpadding.
* **Engineering Solution**:
  Updated the cipher invocation to include `-md sha256`. The backup decrypted cleanly on the first attempt, yielding the complete 154,507-byte plaintext Lua configuration. Documented the implementation in [`scripts/config_crypto.py`](../scripts/config_crypto.py).
* **Key Takeaway**: Cryptographic primitives evolve across tool versions; toolchain evolution (OpenSSL 1.x -> 3.x/4.x) frequently breaks legacy embedded modding scripts due to changed default digest algorithms.

---

### Challenge 4: Client-Side Web UI Modal Lockup on Login
* **Symptom**: Automated browser interactions on `http://192.168.29.1/` resulted in the login screen freezing permanently with a modal overlay: *"Loading Please wait..!"* with an animated GIF, preventing the form submission from completing.
* **Diagnostic Methodology**:
  - Traced client-side JavaScript execution in `mis.js`, `textValidations.js`, and `loadingStatus.js`.
  - Monitored network traffic in browser developer tools: zero HTTP POST requests were dispatched to `/platform.cgi` upon clicking the Login button.
* **Root Cause**:
  The form uses custom jQuery event bindings that trigger `#tf1_pageLoadingOverLay` and `#tf1_pageLoadingMask`. If input events (`keydown`, `blur`, `focus`) are triggered out-of-sequence by automated drivers, the progress bar overlay mounts and blocks all pointer and form events while waiting for an asynchronous callback that never arrives.
* **Engineering Solution**:
  Documented the browser lockup mechanics and established workarounds: executing direct DOM submission via DevTools console (`document.forms[0].submit()`) or hiding the overlay masks (`$("#tf1_pageLoadingOverLay").hide()`), bypassing the stuck timer.
* **Key Takeaway**: Embedded web administration GUIs are often brittle and laden with legacy jQuery scripts; diagnosing client-side DOM events is just as vital as analyzing backend network protocols.

---

### Challenge 5: Direct HTTP POST Rejection (`401 Unauthorized`)
* **Symptom**: Attempting to bypass the broken web UI by issuing direct `curl` POST requests to `/platform.cgi` with administrator credentials returned:
  ```html
  <h1 class="unAuthorised">401 Unauthorized <br>
    <a href="/platform.cgi"> Click here to Relogin </a>
  </h1>
  ```
* **Diagnostic Methodology**:
  - Tested URL-encoded vs raw POST bodies.
  - Inspected response headers: `Transfer-Encoding: chunked`, `Server: Web Server`, no `Set-Cookie` header issued on direct unauthenticated calls.
* **Root Cause**:
  The underlying web daemon on R2.57 enforces strict CSRF and session-state checks. Posting form parameters directly without an initialized session context or valid origin headers is treated as unauthorized.
* **Engineering Solution**:
  Mapped the authentication workflow to require either an active browser session with extracted session cookies or an automated script that mimics the complete initial handshake.
* **Key Takeaway**: Carrier firmware routinely hardens administrative endpoints against raw script automation; authenticated session state must be established before issuing management directives.

---

### Challenge 6: Dual-Homed Network Interface Routing Collision
* **Symptom**: When pushing research commits to GitHub via Git CLI or making external API calls from the host PC, operations hung indefinitely and timed out, despite the PC having an active Wi-Fi internet connection.
* **Diagnostic Methodology**:
  - Inspected network adapters and routing tables via `Get-NetIPInterface` and `Get-NetRoute`.
  - Discovered two active network adapters:
    1. Ethernet (`192.168.29.2`): Connected to isolated workbench router (`192.168.29.1`), Metric = `25`.
    2. Wi-Fi (`192.168.29.84`): Connected to home gateway with Internet, Metric = `35`.
* **Root Cause**:
  Windows selects routes based on the lowest interface metric. Because Ethernet had a lower metric (`25 < 35`), Windows routed all outbound default Internet traffic (`0.0.0.0/0`) out of the Ethernet interface directly into the isolated workbench router, which had no fiber connection and dropped the packets.
* **Engineering Solution**:
  Bound outbound network requests explicitly to the Wi-Fi adapter IP (`--interface 192.168.29.84` in curl) and utilized targeted TCP route binding, ensuring that all GitHub synchronization traffic exited through the Internet gateway while local router communication stayed on Ethernet.
* **Key Takeaway**: Hardware testbenches often feature dual-homed network setups; understanding OS routing metrics is essential to prevent local offline test subnets from intercepting general development traffic.

---

## Technical Summary of Project Deliverables

| Deliverable | Purpose | Technical Validation |
| :--- | :--- | :--- |
| [`scripts/checksum_calculator.py`](../scripts/checksum_calculator.py) | Automated MD5 configuration checksum calculator | Verified against factory ground truth (`7d66...`) |
| [`scripts/config_crypto.py`](../scripts/config_crypto.py) | AES-128-CBC encryption / decryption tool | Validated roundtrip integrity with OpenSSL 4.x |
| [`scripts/r257_signature_bypass_loop.sh`](../scripts/r257_signature_bypass_loop.sh) | Firmware validation interception script | Implements `/tmp/firmCheckRes.txt` spoofing |
| [`docs/HARDWARE_AND_PARTITIONS.md`](HARDWARE_AND_PARTITIONS.md) | Architectural reference of Econet SoC & MTD flash | Maps dual-bank partitions & bootflags |
| [`docs/R257_VS_R215_SECURITY_ANALYSIS.md`](R257_VS_R215_SECURITY_ANALYSIS.md) | Security evolution & anti-rollback comparison | Deep dive into firmware validation daemons |
| [`docs/AI_AGENT_HANDOVER.md`](AI_AGENT_HANDOVER.md) | Interactive state machine & execution guide | Provides actionable handover for future work |

---

## Conclusion & Engineering Value

This project provides concrete, reproducible documentation of firmware security mechanics on the Sercomm JCOW414 platform. By systematically isolating failure points, reverse-engineering parsing boundaries, and documenting cryptographic requirements, this research bridges the gap between vendor lockdowns and open-source embedded software adoption.
