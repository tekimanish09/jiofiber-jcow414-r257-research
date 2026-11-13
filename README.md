# JioFiber Sercomm JCOW414 (Stock Firmware R2.57) to OpenWrt Investigation

[![Hardware: Sercomm JCOW414](https://img.shields.io/badge/Hardware-Sercomm%20JCOW414-blue.svg)](https://en.wikipedia.org/wiki/Sercomm)
[![SoC: Econet EN7528HU](https://img.shields.io/badge/SoC-Econet%20EN7528HU-orange.svg)](https://openwrt.org)
[![Firmware: R2.57](https://img.shields.io/badge/Stock%20Firmware-R2.57-red.svg)]()
[![Target: OpenWrt 23.05](https://img.shields.io/badge/Target-OpenWrt%2023.05-green.svg)](https://openwrt.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **Comprehensive Research Archive & Post-Mortem**: Documenting software-only downgrade attempts, reverse-engineering of configuration encryption & checksums, firmware signature validation roadblocks on stock firmware `R2.57`, and technical pathways to achieve OpenWrt installation.

---

## Executive Summary

This repository documents an intensive investigation into obtaining software-only root access and flashing an unofficial [OpenWrt 23.05 build](https://github.com/Asjohn720/jiofiber-jcow414-openwrt) onto the **Reliance JioFiber Sercomm JCOW414** home gateway (Hardware Revision `0001`, Econet/Airoha EN7528HU platform).

The objective was to repurpose the device as a high-performance, standalone **Dual-Band AC1200 Wi-Fi Access Point and 4-Port Gigabit Ethernet Switch**, operating strictly within a **no-disassembly constraint** (no UART soldering or physical flash programmer).

### Key Findings & Status:
* **The Current Deadlock**: Stock firmware **R2.57** rejects the community-standard **R2.15** downgrade package with:
  ```text
  Firmware file is invalid or corrupted.
  ```
  This is caused by an active firmware validation daemon enforcing anti-rollback and signature checking, not by file corruption.
* **The Checksum Breakthrough**: We successfully reverse-engineered the exact mathematical algorithm used by the router's configuration parser to compute the MD5 digest in `config.checksum`, fixing prior corruption issues in custom configurations.
* **The Interception Loop Vector**: Community research reveals that running a background loop script to blank out `/tmp/firmCheckRes.txt` will bypass the signature check during downgrade—however, this introduces a classic "Catch-22" requiring root shell access prior to the downgrade.
* **Web UI Anomalies**: We identified a client-side JavaScript overlay lockup in the router's web administration panel that causes form submissions to hang under certain browser automation conditions.

---

## 1. Target Hardware & Testbench Environment

```
                      +---------------------------------------+
                      |       Sercomm JCOW414 Router          |
                      |  - SoC: Econet EN7528HU (Dual MIPS)   |
                      |  - RAM: 256 MB / Flash: 128 MB NAND   |
                      |  - Wi-Fi: MT7603E (2.4G) + MT7613BE   |
                      |  - Stock Firmware: R2.57              |
                      |  - IP: 192.168.29.1 (Isolated)        |
                      +---------------------------------------+
                                          |
                                    Cat6 Ethernet
                                 (Direct LAN Link)
                                          |
                      +---------------------------------------+
                      |         Workstation PC                |
                      |  - IP: 192.168.29.2                   |
                      |  - Gateway: 192.168.29.1              |
                      |  - WAN / Fiber Optic: DISCONNECTED   |
                      +---------------------------------------+
```

> **IMPORTANT**: The router was strictly isolated from the fiber optic (GPON) cable throughout all tests to prevent ISP TR-069 remote-management daemons from triggering automated firmware updates or remote configuration overwrites.

---

## 2. Technical Breakthroughs & Reverse Engineering

### 2.1 Configuration Encryption & Decryption (Solves R2.57 `.enc`)
The router exports backups as encrypted `.enc` archives. Decrypting and re-encrypting them requires understanding the exact OpenSSL parameters:

* **Envelope**: Standard OpenSSL salted binary header (`Salted__` followed by 8-byte salt).
* **Cipher**: AES-128-CBC (`aes-128-cbc`).
* **Key Derivation Digest**: Must use **SHA-256** (`-md sha256`).
  *(Note: Older online community scripts specified `-md md5`, which fails with `bad decrypt` on modern OpenSSL 3.x/4.x installations).*

#### CLI Reference:
```bash
# Decrypt backup
openssl aes-128-cbc -d -pass pass:[REDACTED_AES_KEY] -in backup.enc -out config.txt -md sha256

# Re-encrypt modified config
openssl aes-128-cbc -e -pass pass:[REDACTED_AES_KEY] -in config.txt -out backup_modified.enc -md sha256
```
*(A complete Python utility is included in [`scripts/config_crypto.py`](scripts/config_crypto.py)).*

---

### 2.2 Configuration Checksum Algorithm (Solved)
Previous modding attempts frequently encountered restore failures due to declared checksum mismatches. Through byte-level analysis, we determined the exact specification:

1. The configuration file is a plaintext Lua configuration script (~3,144 lines).
2. Near line 3012, a checksum declaration exists:
   ```lua
   config.checksum = "7d669de3e42ace6be9ee2286398e46ca"
   ```
3. **The Hash Boundary**: The MD5 hash is computed across all bytes from offset `0` up to immediately before the string `config.checksum = "`.
4. **Validation Test**:
   - Total pre-checksum bytes: `149,182` bytes.
   - Computed MD5: `7d669de3e42ace6be9ee2286398e46ca`.
   - Result: **100% Exact Match** with the factory declared digest!

We created an automated Python validator and in-place updater in [`scripts/checksum_calculator.py`](scripts/checksum_calculator.py):
```bash
# Check validity
python scripts/checksum_calculator.py config.txt

# Automatically compute and patch checksum into file
python scripts/checksum_calculator.py config.txt --update
```

---

### 2.3 The R2.57 Downgrade Blocker & Root Cause
When attempting to downgrade from stock firmware R2.57 to stock R2.15 using `SRCMTF1_JCOW414_R2.15.img` and `SRCMTF1_JCOW414_R2.15.sig`:

1. Both files pass SHA-256 integrity and contain valid `HDR2` Sercomm image headers:
   * `SRCMTF1_JCOW414_R2.15.img`: `ad2977cca4b2796faa81cf0bf7d6f16b152fffdef1c73aba6b6dabc725bbca97` (38,071,183 bytes)
   * `SRCMTF1_JCOW414_R2.15.sig`: `669961ce8d04cd0e0d14181b49469f87143f190c89ec11f57bac88e14384ea91` (256 bytes)
2. In the web interface (`http://192.168.29.1/`), selecting both files enables the "Update" button.
3. Upon clicking "Update", the router responds with:
   ```text
   Firmware file is invalid or corrupted.
   ```

#### Technical Root Cause:
* Firmware R2.57 implements active anti-rollback rules in its firmware validation daemon.
* When validating older versions, the daemon logs an error code into `/tmp/firmCheckRes.txt`.
* The Web UI checks this file, detects the failure code, and aborts the flash before touching the flash partitions.

#### Community Bypass Solution:
If a root shell is active, running the following loop script intercepts and zeroes out the result file:
```sh
#!/bin/sh
while true; do
    if [ -e /tmp/firmCheckRes.txt ]; then
        cat /dev/null > /tmp/firmCheckRes.txt
    fi
done
```
With this loop running, the Web UI evaluates the signature check as successful and proceeds with the downgrade! *(Script provided in [`scripts/r257_signature_bypass_loop.sh`](scripts/r257_signature_bypass_loop.sh)).*

---

### 2.4 Web Administration UI Anomalies
During automated interaction:
* The login form is managed by `mis.js` and `textValidations.js`.
* When clicking the login submit button, a loading dialog (`#tf1_pageLoadingOverLay`) activates.
* If browser automation triggers events out-of-order, the loading modal locks the viewport and fails to dispatch the underlying form POST to `platform.cgi`.
* Direct unauthenticated HTTP POST requests to `platform.cgi` return `401 Unauthorized`.

---

## 3. Flash Partition Architecture & Dual-Bank Boot

The JCOW414 utilizes a dual-bank MTD layout on 128 MB SPI NAND flash:

| MTD Partition | Label | Role in Modding |
| :--- | :--- | :--- |
| `/dev/mtd4` | `tclinux` | **Bank 1**: Primary boot partition (Target for OpenWrt TRX) |
| `/dev/mtd5` | `tclinux_data` | RootFS data overlay (SquashFS / JFFS2) |
| `/dev/mtd7` | `tclinux_slave` | **Bank 2**: Secondary / Fallback partition (Stock R2.15 backup) |
| `/dev/mtd8` | `tclinux_slave_data` | Secondary data overlay |

### Dual-Bank Boot Swap Utility:
The underlying Sercomm Linux system includes a proprietary boot-flag utility:
```sh
/usr/bin/sys bootflag swap
```
This command swaps the active boot pointer between Bank 1 (`mtd4`) and Bank 2 (`mtd7`).

---

## 4. OpenWrt Community Build Details

* **Build Artifact**: `openwrt-jiofiber_jcow414_v1.1.trx`
* **File Size**: 10,223,616 bytes (~10.2 MB)
* **SHA-256 Digest**:
  ```text
  43112eacecdcea64bb213520df50df18cbcd68fc4682932807e915e97883feb2
  ```
* **Build String**: `OpenWrt-Asjohn720-r0-c4526c7`
* **Base System**: OpenWrt 23.05 (Target: `econet/en7528`)
* **Hardware Capabilities in OpenWrt**:
  - ✅ All 4 Gigabit Ethernet LAN ports bridged into `br-lan` (Full Duplex 1 Gbps)
  - ✅ 2.4 GHz Wi-Fi (MediaTek MT7603E)
  - ✅ 5 GHz Wi-Fi (MediaTek MT7613BE)
  - ✅ USB 2.0 / USB 3.0 storage support
  - ✅ Web UI (LuCI) accessible at `192.168.1.1`
  - ❌ GPON Optical Uplink (Unsupported - AP mode only)

---

## 5. Next Steps for Community Researchers

If you have a Sercomm JCOW414 running firmware R2.57 and want to advance this work:

1. **Hardware Serial (UART) Access**:
   - Connecting a 3.3V USB-to-TTL serial adapter to the internal UART headers bypasses the web UI lock and grants an instant root shell.
   - From UART, run `scripts/r257_signature_bypass_loop.sh &`, then trigger the downgrade to R2.15 via the web UI or write the TRX directly using `mtd -f write`.
2. **Configuration Restore Vector**:
   - Test whether restoring `backup_modified.enc` (with valid MD5 checksum) successfully executes the `telnetd` spawn command on boot in your specific hardware revision.
3. **Firmware Decryption / Header Spoofing**:
   - Investigate whether the header of `SRCMTF1_JCOW414_R2.15.img` can have its version string edited to match or exceed `R2.57` while remaining structurally acceptable to the bootloader.

---

## Repository Structure

```text
├── README.md                           # Master investigation report (this document)
├── LICENSE                             # MIT License
├── docs/
│   ├── HARDWARE_AND_PARTITIONS.md      # Detailed MTD layout and hardware breakdown
│   └── R257_VS_R215_SECURITY_ANALYSIS.md # Deep-dive security & signature comparison
└── scripts/
    ├── checksum_calculator.py          # Standalone MD5 checksum calculator & updater
    ├── config_crypto.py                # AES-128-CBC encryption/decryption tool
    └── r257_signature_bypass_loop.sh   # Firmware signature bypass loop script
```

---

## Contributing & Community Credits

* Research and documentation based on community contributions from **itsyourap** ([JF-Customisation](https://github.com/JFC-Group/JF-Customisation)), **Asjohn720** ([jiofiber-jcow414-openwrt](https://github.com/Asjohn720/jiofiber-jcow414-openwrt)), and **Naitik1208** ([JF-ROUTER](https://github.com/Naitik1208/JF-ROUTER)).
* Pull requests, additional serial console logs, and partition dumps are warmly welcomed!

## Disclaimer

*This project is for educational and interoperability research purposes only. Flashing custom firmware carries inherent risks of permanent device bricking. Authors and contributors are not responsible for any hardware damage.*
