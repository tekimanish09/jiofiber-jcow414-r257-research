# AI Agent Handover & Session State Document

> [STOP] **MANDATORY OPERATING DIRECTIVE FOR RESUMING AI AGENTS**:  
> **DO NOT REPEAT THE AUTHOR'S MISTAKES.**  
> The author of this repository ("aka tekimanish09") spent over 9 continuous hours discovering and testing the boundaries of stock firmware R2.57. Every failure documented in **Section 0** is an established, proven hard stop.  
> If you encounter, consider, or are asked to attempt any of these known failure paths, you **MUST EXPLICITLY REPORT IT TO THE USER**, quoting:  
> *"The author of this repository ('aka tekimanish09') also faced this exact issue [quote the specific roadblock/error], so we are going to avoid this mistake and take [alternative path]."*

---

## 0. Blacklist of Proven Mistakes & Anti-Patterns (DO NOT RETRY!)

| # | Proven Mistake / Deadlock | What Happens | Why It Fails | Mandatory Quote to User & What to Do Instead |
| :--- | :--- | :--- | :--- | :--- |
| **1** | **Blind Web UI Downgrade to R2.15** | Router UI displays: `Firmware file is invalid or corrupted.` | Stock R2.57 runs a background validation daemon that enforces anti-rollback and checks signatures, writing failure codes to `/tmp/firmCheckRes.txt`. | **Quote to User**: *"The author of this repository ('aka tekimanish09') also faced 'Firmware file is invalid or corrupted' when uploading R2.15 directly. We know R2.57 rejects older images at the daemon level, so we are avoiding blind re-uploads. Instead, we must gain shell access first to run the `/tmp/firmCheckRes.txt` bypass loop, or flash via MTD directly."* |
| **2** | **Restoring Config with Unmatched / Uncalculated Checksum** | Router rejects `.enc` restore or discards injected lines. | The parser verifies a 32-character MD5 checksum across all bytes from byte `0` to line 3012. Any change to line 1 invalidates the stock MD5. | **Quote to User**: *"The author of this repository ('aka tekimanish09') spent extensive time resolving config restore rejections caused by MD5 mismatches. We are not restoring raw modified files without verifying their exact MD5 using `checksum_calculator.py`. We already generated `modified_correct_JCOW414.enc` with a verified MD5 for this reason."* |
| **3** | **Spamming Direct unauthenticated curl POST to `/platform.cgi`** | Returns `401 Unauthorized` or empty chunked response. | Router requires active browser session tracking and session headers; unauthenticated POST requests are dropped by the web daemon. | **Quote to User**: *"The author of this repository ('aka tekimanish09') tested unauthenticated direct POST requests to `/platform.cgi` and verified they consistently return 401 Unauthorized. We are avoiding blind POST scripts and will use an authenticated browser session."* |
| **4** | **Hanging on Browser Modal Loading Overlay** | Automated browsers freeze indefinitely on *"Loading Please wait..!"* with a spinning GIF. | Client-side JavaScript (`loadingStatus.js`) overlay `#tf1_pageLoadingOverLay` locks the DOM and fails to dispatch the underlying form POST if event listeners are desynchronized. | **Quote to User**: *"The author of this repository ('aka tekimanish09') discovered that the web panel's loading overlay hangs indefinitely in automated browsers. We are avoiding waiting on the UI spinner and will dispatch the form submission directly or dismiss the overlay via console."* |
| **5** | **Plugging in the GPON Fiber Optic Cable** | Router auto-updates firmware or wipes custom configuration. | Jio TR-069 ACS remote-management automatically pushes operator policy when connected to the ISP optical distribution network. | **Quote to User**: *"The author of this repository ('aka tekimanish09') explicitly kept the fiber cable unplugged to prevent TR-069 from reverting changes or locking down the device. Keep the optical fiber disconnected."* |
| **6** | **Routing Internet / GitHub Operations via the Ethernet Adapter** | Commands like `git push` or external HTTP calls hang or timeout. | The Ethernet adapter has default gateway `192.168.29.1` (the offline workbench router), which has no WAN connectivity. | **Quote to User**: *"The author of this repository ('aka tekimanish09') found that Windows defaults outbound internet traffic to the offline Ethernet router, causing timeouts. We must bind internet operations to the Wi-Fi adapter (`192.168.29.84`)."* |

---

## 1. System & Device Profile

* **Target Device**: Reliance JioFiber Sercomm JCOW414 Home Gateway
* **Hardware Revision**: `0001`
* **SoC Platform**: Airoha / Econet EN7528HU (Dual-core MIPS 1004Kc @ 900 MHz)
* **Stock Firmware**: `SRCMTF1_JCOW414_R2.57` (Stock R2.57)
* **Target OpenWrt Build**: `openwrt-jiofiber_jcow414_v1.1.trx` (OpenWrt 23.05 community port by Asjohn720)
* **Network Setup**:
  - Router IP: `192.168.29.1`
  - Host PC Ethernet IP: `192.168.29.2` (Subnet: `255.255.255.0`, Gateway: `192.168.29.1`)
  - Connection Type: Direct RJ45 Cat6 cable to LAN Port 1.
  - Optical WAN / GPON: **Physically Disconnected** (Critical to block ISP TR-069 auto-upgrades).
* **Credentials & Keys**:
  - Web Admin Username: `admin`
  - Web Admin Password: `[REDACTED_PASSWORD]`
  - AES Config Passphrase: Saved in local `key.txt` (Derived via reverse-engineered Sercomm key derivation).

---

## 2. Local Filesystem Map on Host Machine

All project assets are organized under `D:\#IMPPPPPPPPPPPPPPPPPPPPPPPP\`:

```text
D:\#IMPPPPPPPPPPPPPPPPPPPPPPPP|-- #FURTHER_IMPP - Copy\                     # Configuration reverse-engineering workspace
|   |-- RSVOTCXXXXXXXX_JCOW414.enc            # Original factory encrypted configuration backup
|   |-- RSVOTCXXXXXXXX_JCOW414.txt            # Decrypted original configuration (LF line endings)
|   |-- key.txt                               # Local AES key for this router (Passphrase)
|   |-- modified_correct.txt                  # Modified plaintext config with VALID MD5 checksum
|   |-- modified_correct_JCOW414.enc          # Encrypted modified config ready for restore (Salted__)
|   |-- RSVOTCXXXXXXXX_JCOW414_modified.enc   # Same encrypted file renamed to original backup format
|   \-- keyguesser_6a46fe0c.py                # Local keyguesser script
|
|-- Firmware-JCOW414_2.15\                    # Firmware packages
|   |-- SRCMTF1_JCOW414_R2.15.img             # Stock R2.15 firmware image (38,071,183 bytes)
|   |-- SRCMTF1_JCOW414_R2.15.sig             # Stock R2.15 cryptographic signature (256 bytes)
|   \-- openwrt-jiofiber_jcow414_v1.1.trx     # OpenWrt factory image (10,223,616 bytes)
|
\-- jiofiber-jcow414-r257-research\           # This repository (Git tracked)
    |-- README.md                             # Master investigation report & portfolio showcase
    |-- LICENSE                               # MIT Open-Source License
    |-- docs/
    |   |-- PORTFOLIO_CASE_STUDY.md           # Engineering portfolio case study & problem log
    |   |-- AI_AGENT_HANDOVER.md              # (This document)
    |   |-- CHRONOLOGICAL_LOG_AND_ERRORS.md   # Full network, header, and diagnostic logs
    |   |-- HARDWARE_AND_PARTITIONS.md        # Detailed MTD layout and hardware breakdown
    |   |-- R257_VS_R215_SECURITY_ANALYSIS.md # Deep-dive security & signature comparison
    |   \-- jcow414_openwrt_session_archive(Till Now).md # Sanitized raw investigation session archive
    |-- firmware/                             # Firmware artifacts & target OpenWrt image
    |   |-- SRCMTF1_JCOW414_R2.15.img         # Stock R2.15 firmware image (38 MB)
    |   |-- SRCMTF1_JCOW414_R2.15.sig         # Stock R2.15 companion signature (256 bytes)
    |   \-- openwrt-jiofiber_jcow414_v1.1.trx # OpenWrt 23.05 factory squashfs image (10.2 MB)
    |-- scripts/
    |   |-- checksum_calculator.py            # Standalone MD5 checksum calculator & updater
    |   |-- config_crypto.py                  # AES-128-CBC encryption/decryption tool
    |   \-- r257_signature_bypass_loop.sh     # Firmware signature bypass loop script
    \-- templates/
        |-- config_injection_template.txt     # Reference template for Lua command injection
        \-- keyguesser_template.py            # Generic AES key derivation script
```

---

## 3. Verified Technical Status & Progress Matrix

| Component / Vector | Status | Technical Details |
| :--- | :--- | :--- |
| **Direct Ping Connectivity** | [SUCCESS] **SUCCESS** | Host (`192.168.29.2`) pings router (`192.168.29.1`) with `<1ms` latency. |
| **Port Status** | [INFO] **OBSERVED** | TCP 80 (HTTP), 443 (HTTPS), 8080 (HTTP-Alt) are **OPEN**; TCP 23 (Telnet), 22 (SSH) are **CLOSED**. |
| **Config Decryption** | [SUCCESS] **SOLVED** | Decryption command: `openssl aes-128-cbc -d -pass pass:<KEY> -in <ENC> -out <TXT> -md sha256`. |
| **Config MD5 Checksum** | [SUCCESS] **SOLVED** | Verified: MD5 across byte 0 to immediately before `config.checksum = "`. Stock checksum `7d66...` verified 100%. |
| **Modified Config Payload** | [SUCCESS] **READY** | `modified_correct.txt` has valid MD5 (`1cf7898852d9b5b9303be87bcd6aff4f`) and line 1 injection payload. |
| **Web UI Direct Downgrade** | [BLOCKED] **BLOCKED** | Uploading R2.15 `.img` + `.sig` via Web UI returns *"Firmware file is invalid or corrupted"*. |
| **Downgrade Bypass Logic** | [INFO] **MAPPED** | Validation error is written to `/tmp/firmCheckRes.txt`. Looping `cat /dev/null > /tmp/firmCheckRes.txt` bypasses it, but requires a root shell. |
| **Web UI Login Form Hang** | [WARNING] **WORKAROUND NEEDED** | Web automation triggers client-side `#tf1_pageLoadingOverLay` ("Loading Please wait..!") which occludes form and delays POST. Direct unauthenticated curl POST returns `401 Unauthorized`. |

---

## 4. The Exact Next Moves for the Resuming Agent

To reach the end goal (OpenWrt installed and router functioning as AP), choose one of the following primary routes:

### Route 1: Restore the Verified Modified Configuration (Software Route)
The file `D:\#IMPPPPPPPPPPPPPPPPPPPPPPPP\#FURTHER_IMPP - Copy\modified_correct_JCOW414.enc` has a **mathematically valid MD5 checksum** and contains the Lua injection on line 1:
```lua
config.userdb = {} os.execute("/usr/sbin/telnetd"); os.execute("/pfrm2.0/bin/iptables -I fwInBypass -p tcp --dport 23 -m ifgroup --ifgroup-in 0x1/0x1 -j ACCEPT"); os.execute("echo -e \"[ROOT_PWD]\n[ROOT_PWD]\" | passwd root");
```

**Steps to Execute**:
1. Open the router admin panel (`http://192.168.29.1/`) in a real browser (Chrome / Edge).
2. Log in with the administrator password.
   *(Note: If the loading overlay hangs, open DevTools console (`F12`) and run `$("#tf1_pageLoadingOverLay, #tf1_pageLoadingMask").hide(); document.forms[0].submit();`).*
3. Navigate to **Maintenance** -> **Backup / Restore** (`backupRestore.html`).
   *(If the menu item is hidden in R2.57, inspect DOM or navigate to `http://192.168.29.1/platform.cgi?page=backupRestore.html`).*
4. Upload `modified_correct_JCOW414.enc` and submit Restore.
5. Once the router processes the configuration and reboots:
   - Check if port 23 is open: `Test-NetConnection -ComputerName 192.168.29.1 -Port 23`
   - Log into root shell via Telnet: `telnet 192.168.29.1`

---

### Route 2: Execute Firmware Downgrade (Once Shell Access is Achieved)
Once a root shell is open (via Telnet from Route 1 or UART):

1. **Deploy the Signature Bypass Loop**:
   Run the loop script to suppress firmware rejection:
   ```sh
   while true; do
       if [ -e /tmp/firmCheckRes.txt ]; then
           cat /dev/null > /tmp/firmCheckRes.txt
       fi
   done &
   ```
2. **Trigger the Downgrade**:
   - Go to Web UI -> Maintenance -> Firmware Upgrade.
   - Upload `SRCMTF1_JCOW414_R2.15.img` and `SRCMTF1_JCOW414_R2.15.sig`.
   - Click Upgrade. The verification check will pass because `/tmp/firmCheckRes.txt` is continually wiped.
3. The router reboots into stock `R2.15`.

---

### Route 3: Direct OpenWrt Flash via Root Shell (Bypassing Downgrade)
If you already have a root shell on R2.57, you can flash the OpenWrt TRX image directly without downgrading to R2.15:

1. Transfer `openwrt-jiofiber_jcow414_v1.1.trx` to the router's `/tmp`:
   ```sh
   # On host PC: start simple HTTP server
   python -m http.server 8000
   
   # In router root shell:
   cd /tmp
   wget http://192.168.29.2:8000/openwrt-jiofiber_jcow414_v1.1.trx
   ```
2. Verify image integrity in `/tmp`:
   ```sh
   md5sum openwrt-jiofiber_jcow414_v1.1.trx
   ```
3. Flash the TRX image into Bank 1 (`tclinux` / `mtd4`):
   ```sh
   mtd -f write openwrt-jiofiber_jcow414_v1.1.trx tclinux
   ```
4. Swap the active boot flag to the new image:
   ```sh
   /usr/bin/sys bootflag swap
   ```
5. Reboot the router:
   ```sh
   reboot
   ```
6. **Post-Boot**: The router will boot OpenWrt 23.05 with LuCI web interface at `http://192.168.1.1/` (Change host PC IP to `192.168.1.2`, subnet `255.255.255.0`).

---

## 5. Security & Verification Directives

1. **Keep GPON Fiber Cable Disconnected**: Under no circumstances connect the optical WAN fiber cable to the router during this process. Doing so allows the ISP TR-069 ACS server to push automated firmware updates and overwrite custom configurations.
2. **Preserve Network Isolation**: The host PC must maintain its dual-homed configuration (Ethernet on `192.168.29.2` for router testing; Wi-Fi on `192.168.29.84` for internet access). Outbound internet/Git commands must be explicitly directed through the Wi-Fi interface.
3. **Verify All Checksums**: Before restoring any configuration, always verify the MD5 checksum using `python scripts/checksum_calculator.py <filename>`. Never flash a configuration file with an unverified checksum.
