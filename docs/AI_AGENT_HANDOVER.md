# AI Agent Handover & Session State Document

> **Notice to AI Agent / Engineer Resuming This Work**:
> This document details the exact state of the environment, local filesystem layout, tested attack vectors, validated breakthroughs, and recommended execution routes. Read this document first before taking any action.

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

---

## 2. Local Filesystem Map on Host Machine

All project assets are organized under `D:\#IMPPPPPPPPPPPPPPPPPPPPPPPP\`:

```text
D:\#IMPPPPPPPPPPPPPPPPPPPPPPPP\
â”œâ”€â”€ #FURTHER_IMPP - Copy\                     # Configuration reverse-engineering workspace
â”‚   â”œâ”€â”€ RSVOTCXXXXXXXX_JCOW414.enc           # Original factory encrypted configuration backup
â”‚   â”œâ”€â”€ RSVOTCXXXXXXXX_JCOW414.txt           # Decrypted original configuration (LF line endings)
â”‚   â”œâ”€â”€ key.txt                               # Local AES key for this router (Passphrase)
â”‚   â”œâ”€â”€ modified_correct.txt                  # Modified plaintext config with VALID MD5 checksum
â”‚   â”œâ”€â”€ modified_correct_JCOW414.enc          # Encrypted modified config ready for restore (Salted__)
â”‚   â”œâ”€â”€ RSVOTCXXXXXXXX_JCOW414_modified.enc  # Same encrypted file renamed to original backup format
â”‚   â””â”€â”€ keyguesser_6a46fe0c.py                # Local keyguesser script
â”‚
â”œâ”€â”€ Firmware-JCOW414_2.15\                    # Firmware packages
â”‚   â”œâ”€â”€ SRCMTF1_JCOW414_R2.15.img             # Stock R2.15 firmware image (38,071,183 bytes)
â”‚   â”œâ”€â”€ SRCMTF1_JCOW414_R2.15.sig             # Stock R2.15 cryptographic signature (256 bytes)
â”‚   â””â”€â”€ openwrt-jiofiber_jcow414_v1.1.trx     # OpenWrt factory image (10,223,616 bytes)
â”‚
â”œâ”€â”€ jiofiber-jcow414-r257-research\           # This repository (Git tracked)
â”‚   â”œâ”€â”€ README.md
â”‚   â”œâ”€â”€ docs/
â”‚   â”‚   â”œâ”€â”€ AI_AGENT_HANDOVER.md              # (This document)
â”‚   â”‚   â”œâ”€â”€ HARDWARE_AND_PARTITIONS.md
â”‚   â”‚   â”œâ”€â”€ R257_VS_R215_SECURITY_ANALYSIS.md
â”‚   â”‚   â””â”€â”€ CHRONOLOGICAL_LOG_AND_ERRORS.md
â”‚   â”œâ”€â”€ scripts/
â”‚   â”‚   â”œâ”€â”€ checksum_calculator.py
â”‚   â”‚   â”œâ”€â”€ config_crypto.py
â”‚   â”‚   â””â”€â”€ r257_signature_bypass_loop.sh
â”‚   â””â”€â”€ templates/
â”‚       â”œâ”€â”€ config_injection_template.txt
â”‚       â””â”€â”€ keyguesser_template.py
```

---

## 3. Verified Technical Status & Progress Matrix

| Component / Vector | Status | Technical Details |
| :--- | :--- | :--- |
| **Direct Ping Connectivity** | âœ… **SUCCESS** | Host (`192.168.29.2`) pings router (`192.168.29.1`) with `<1ms` latency. |
| **Port Status** | â„¹ï¸ **OBSERVED** | TCP 80 (HTTP), 443 (HTTPS), 8080 (HTTP-Alt) are **OPEN**; TCP 23 (Telnet), 22 (SSH) are **CLOSED**. |
| **Config Decryption** | âœ… **SOLVED** | Decryption command: `openssl aes-128-cbc -d -pass pass:<KEY> -in <ENC> -out <TXT> -md sha256`. |
| **Config MD5 Checksum** | âœ… **SOLVED** | Verified: MD5 across byte 0 to immediately before `config.checksum = "`. Stock checksum `7d66...` verified 100%. |
| **Modified Config Payload** | âœ… **READY** | `modified_correct.txt` has valid MD5 (`1cf7898852d9b5b9303be87bcd6aff4f`) and line 1 injection payload. |
| **Web UI Direct Downgrade** | âŒ **BLOCKED** | Uploading R2.15 `.img` + `.sig` via Web UI returns *"Firmware file is invalid or corrupted"*. |
| **Downgrade Bypass Logic** | â„¹ï¸ **MAPPED** | Validation error is written to `/tmp/firmCheckRes.txt`. Looping `cat /dev/null > /tmp/firmCheckRes.txt` bypasses it, but requires a root shell. |
| **Web UI Login Form Hang** | âš ï¸ **WORKAROUND NEEDED** | Web automation triggers client-side `#tf1_pageLoadingOverLay` ("Loading Please wait..!") which occludes form and delays POST. Direct unauthenticated curl POST returns `401 Unauthorized`. |

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
6. Post-Boot: The router will boot OpenWrt 23.05 with LuCI web interface at `http://192.168.1.1/` (Change host PC IP to `192.168.1.2`).

---

## 5. Important Guardrails for the Resuming Agent

* â›” **DO NOT connect the GPON Fiber cable**: TR-069 auto-management will immediately patch any open vectors or revert firmware.
* â›” **DO NOT blindly re-upload R2.15 in the Web UI** without the `/tmp/firmCheckRes.txt` bypass loop runningâ€”it will always fail with *"invalid or corrupted"*.
* â›” **DO NOT overwrite `RSVOTCXXXXXXXX_JCOW414.txt` or `key.txt`**â€”they are the clean recovery ground truth.
* âš ï¸ **When pushing to GitHub**: Ensure Windows routes traffic via Wi-Fi (`--interface 192.168.29.84` or bound interface) so requests don't attempt to route out the offline Ethernet gateway.

