# Hardware Architecture & Flash Partition Layout

## 1. System Specifications

| Component | Specification | Notes |
| :--- | :--- | :--- |
| **Model** | Sercomm JCOW414 | Also shares architecture with JCO4032 / JCOW404 / JCOW411 |
| **Vendor** | Reliance Jio Infocomm Ltd. / Sercomm Corp. | Manufactured for JioFiber FTTH deployments |
| **Hardware Revision** | `0001` | Standard production revision |
| **SoC (System-on-Chip)** | Airoha / Econet EN7528HU | Dual-core MIPS 1004Kc @ 900 MHz (MediaTek subsidiary) |
| **RAM** | 256 MB DDR3 | Adequate for OpenWrt 23.05 + LuCI + basic packages |
| **Flash Memory** | 128 MB SPI NAND Flash | Dual-bank layout for firmware images |
| **2.4 GHz Wi-Fi** | MediaTek MT7603E | 802.11b/g/n, 2x2:2 MIMO, up to 300 Mbps |
| **5 GHz Wi-Fi** | MediaTek MT7613BE | 802.11a/n/ac Wave 2, 2x2:2 MU-MIMO, up to 867 Mbps |
| **LAN Switch** | Integrated Gigabit Ethernet | 4x 10/100/1000 Mbps RJ45 ports |
| **WAN (Optical)** | GPON (Gigabit Passive Optical Network) | SC/APC fiber interface (unsupported in OpenWrt build) |
| **Voice / VoIP** | 1x FXS RJ11 Port | Unsupported in community OpenWrt |
| **USB** | 1x USB 2.0 / 3.0 Port | Supported in OpenWrt with `kmod-usb-storage` |

---

## 2. Flash Partition Layout (MTD)

The Econet EN7528 platform on Sercomm JCOW414 implements a **dual-bank system** designed for safe Over-The-Air (OTA) updates and rollback protection:

```
+-------------------------------------------------------------+
| MTD0: bootloader (U-Boot / Econet Bootloader)               |
+-------------------------------------------------------------+
| MTD1: romfile (Default factory settings & calibration)      |
+-------------------------------------------------------------+
| MTD2: nvram (Persistent device settings & MAC/Serial)       |
+-------------------------------------------------------------+
| MTD3: config (User runtime configuration)                   |
+-------------------------------------------------------------+
| MTD4: tclinux (Bank 1: Primary Kernel + RootFS SquashFS)    |  <-- OpenWrt Target
+-------------------------------------------------------------+
| MTD5: tclinux_data (Bank 1: JFFS2 / OverlayFS user data)    |
+-------------------------------------------------------------+
| MTD6: reserve / crashlog                                    |
+-------------------------------------------------------------+
| MTD7: tclinux_slave (Bank 2: Secondary / Fallback firmware) |  <-- Stock R2.15 Fallback
+-------------------------------------------------------------+
| MTD8: tclinux_slave_data (Bank 2: Data)                     |
+-------------------------------------------------------------+
```

### Partition Highlights:
* **Primary Bank (`mtd4: tclinux`)**: The active runtime partition where stock firmware executes by default.
* **Secondary Bank (`mtd7: tclinux_slave`)**: The secondary partition used during vendor updates.
* **Boot Selection & Swap Utility**:
  The underlying Sercomm Linux environment includes a proprietary boot-flag utility:
  ```sh
  /usr/bin/sys bootflag swap
  ```
  Executing this command toggles the active boot partition pointer in NVRAM between Bank 1 (`tclinux`) and Bank 2 (`tclinux_slave`).

---

## 3. Firmware Container Format (`HDR2`)

Both the official Sercomm vendor firmware images (`SRCMTF1_JCOW414_R2.15.img`) and the community OpenWrt build (`openwrt-jiofiber_jcow414_v1.1.trx`) utilize the **HDR2 container format**:

- **Magic Bytes**: Offset `0x00000000` starts with ASCII `HDR2` (`0x48 0x44 0x52 0x32`).
- **Internal Offsets in Stock R2.15**:
  - `0x1c`: Version string (`2.15`)
  - `0x34`: Vendor ID (`Reliance`)
  - `0x74`: Image filename (`Reliance_v2.15.img`)
  - `0x100`: Second `HDR2` container header
  - `0x110`: Target platform identifier (`JCOW414_R2.15`)
- **Internal Offsets in OpenWrt TRX**:
  - `0x00`: `HDR2` header
  - `0x10`: Build signature (`OpenWrt-Asjohn720-r0-c4526c7`)
  - Contains standard OpenWrt `rootfs` and `rootfs_data` SquashFS markers.

---

## 4. Hardware Repurposing: Access Point / Switch Mode

Because OpenWrt does not include proprietary proprietary Econet GPON optical MAC drivers:
1. **GPON WAN is disabled**: The router cannot replace your ISP fiber ONT directly.
2. **Access Point / Switch Mode**:
   - All four LAN ports (`eth0`, `eth1`, `eth2`, `eth3`) are bridged into `br-lan`.
   - Connect an Ethernet cable from your existing main home router/gateway into LAN Port 1.
   - The JCOW414 functions as a high-performance Gigabit Ethernet switch and simultaneous Dual-Band AC1200 Wi-Fi Access Point running native OpenWrt 23.05 with full LuCI, VLAN support, and firewall capabilities.
