# Stock Firmware Security Analysis: R2.15 vs R2.57

## 1. Overview of Firmware Evolutions

| Feature / Mechanism | Stock Firmware R2.15 | Stock Firmware R2.57 | Impact on Modding / OpenWrt |
| :--- | :--- | :--- | :--- |
| **Release Era** | Early JioFiber deployment (~2019-2020) | Later security rollout (~2022-2024+) | Hardened against known public exploits |
| **Downgrade / Anti-Rollback** | Allowed via Web UI (`.img` + `.sig`) | **Strictly blocked** ("Invalid or corrupted") | Stock UI rejects R2.15 downgrade without bypass |
| **Firmware Signature Check** | Relies on older vendor public key | Re-keyed or checks minimum firmware level | Generates error in `/tmp/firmCheckRes.txt` |
| **Config Backup Encryption** | AES-128-CBC (derived from Serial/SSID) | AES-128-CBC (Same key derivation, but stricter) | Requires `-md sha256` in modern OpenSSL |
| **Config Lua Execution Vector** | Commands executed before checksum fail | Execution behavior patched or restricted | Requires mathematically valid MD5 checksum |
| **Telnet Daemon (`telnetd`)** | Can be started via config restore | Disabled by watchdog (`/flash/telnetDisable`) | Watchdog kills telnet unless flag is removed |
| **TR-069 Remote Management** | Active when connected to fiber | Active; can push silent forced upgrades | Device **must** stay disconnected from WAN |

---

## 2. Deep Dive: The Downgrade Validation Gate

When uploading `SRCMTF1_JCOW414_R2.15.img` and its companion `SRCMTF1_JCOW414_R2.15.sig` through the stock web interface at `http://192.168.29.1/`:

1. The client browser uploads both files to `platform.cgi`.
2. The router's CGI backend invokes the internal firmware validation binary (commonly `firmCheck` or a daemon in `/pfrm2.0/bin/`).
3. The binary:
   - Validates the `HDR2` container structure.
   - Extracts the image version string `2.15`.
   - Compares the target version against the currently installed running version (`2.57`).
   - Verifies the cryptographic RSA/ECC signature against the onboard public key stored in flash.
4. **The Failure Point**:
   Because `2.15 < 2.57` (anti-rollback) or because the public key rotated in later releases, the validation utility writes an error code into `/tmp/firmCheckRes.txt`.
5. The web interface reads `/tmp/firmCheckRes.txt`, detects a non-zero/error result, and immediately halts the flash process, displaying:
   ```text
   Firmware file is invalid or corrupted.
   ```

### The `/tmp/firmCheckRes.txt` Interception Loop:
Community researchers discovered that if root shell access is available, running:
```sh
while true; do
    if [ -e /tmp/firmCheckRes.txt ]; then
        cat /dev/null > /tmp/firmCheckRes.txt
    fi
done
```
causes the CGI handler to find an empty/successful result file, effectively tricking the firmware updater into proceeding with the downgrade flash!

---

## 3. Deep Dive: Configuration Checksum Reverse Engineering

### Checksum Specification:
* **Algorithm**: Standard MD5 (RFC 1321).
* **Format**: 32-character hexadecimal lowercase string.
* **Location**: Embedded in the decrypted configuration text file, typically at line 3012:
  ```lua
  config.checksum = "7d669de3e42ace6be9ee2286398e46ca"
  ```
* **Exact Calculation Boundary**:
  The MD5 digest is computed across all bytes from byte offset `0` of the file up to the exact byte immediately preceding the string `config.checksum = "`.
  This includes the newline character (`0x0A` or `\n`) on the preceding line.

```
Byte 0                                         Offset N (e.g., 149182)
[---------------------- RAW CONFIG BYTES ----------------------]\nconfig.checksum = "<MD5>"
|<------------------- MD5 COMPUTED OVER THIS ----------------->|
```

### Verification Proof:
* Raw file size: 154,507 bytes
* Checksum line offset: byte 149,182
* Data hashed: 149,182 bytes
* Resulting MD5: `7d669de3e42ace6be9ee2286398e46ca` (100% exact match against declared stock checksum).

---

## 4. Web UI Anomaly: The Client-Side Freeze

During programmatic and headless browser exploration on R2.57:
* The login form uses JavaScript event listeners in `mis.js` and `textValidations.js`.
* When clicking the "Login" button, a modal loading mask (`#tf1_pageLoadingOverLay` and `#tf1_pageLoadingMask`) is displayed with the text *"Loading Please wait..!"*.
* In automated/scripted browser sessions, if the input field blur/focus events or timing differ from a live user typing, the script triggers the loading overlay but fails to dispatch the underlying form POST to `platform.cgi`, causing the UI to freeze indefinitely.
* Direct POST requests sent via tools like `curl` without full session context or valid origin headers return `401 Unauthorized`.
