---
title: "Sercomm JCOW414 JioFiber R2.57 â†’ OpenWrt Investigation Archive"
status: "BLOCKED â€” downgrade rejected; no firmware or configuration modification applied; session paused"
repositories:
  - "https://github.com/Asjohn720/jiofiber-jcow414-openwrt"
key_technologies:
  - "Sercomm JCOW414; JioFiber stock firmware R2.57 / target R2.15"
  - "OpenWrt 23.05 community build; Airoha / Econet EN7528HU platform"
  - "Windows; Ethernet; IPv4; ICMP; TCP/23 Telnet"
  - "HTTP-based router administration / backup-restore form"
  - "OpenSSL; Winget; encrypted router configuration (.enc); plaintext configuration"
  - "IMG/SIG firmware pair; TRX firmware image; HDR2 container marker"
  - "MTD flash partitions; dual-bank boot selection (repository claims)"
  - "MD5 configuration checksum; SHA-256 artifact integrity checks"
archive_metadata:
  conversation_date_range: "2026-11-12 to 2026-11-13 (Asia/Kolkata; precise per-message timestamps unavailable)"
  archive_scope: "Reconstructed from retained conversation notes, tool results, and files mounted in the active session. Not a literal export of every chat message."
  sensitive_data_policy: "Passwords, session tokens, encryption keys, and executable command-injection payloads are not reproduced. Their presence and role are documented where relevant."
---

# 1. Executive State & Trajectory

## Starting Point

- **Goal:** Obtain software-only root access to the user's own JioFiber Sercomm JCOW414 router, install an unofficial OpenWrt build, then use the device as an Ethernet/Wi-Fi access point.
- **Explicit constraints:** No UART, soldering, serial-console hardware, or other physical modification. The user wanted a software-only route. The router was isolated on a workbench, connected only to a Windows PC by Ethernet and to power.
- **Router identity:**
  - Manufacturer/platform reported: Sercomm.
  - Model: `JCOW414`.
  - Hardware version: `0001`.
  - Stock firmware at the start and at the end: `R2.57`.
  - Router administration address: `192.168.29.1`.
- **PC/network state:**
  - Windows PC Ethernet IPv4 address: `192.168.29.2`.
  - Router responded to ping.
  - TCP port 23 (Telnet) was checked and found closed before any modified configuration was restored.
- **Initial assumptions under investigation:**
  - The newly published GitHub project might provide a no-disassembly downgrade-and-flash path.
  - The project's first step appeared to require an R2.15 firmware `.img` and companion `.sig` file.
  - The repo's `.trx` file appeared intended for the JCOW414.
  - A decrypted configuration backup might help understand the stock configuration format and the router's supported management settings.

## Current State

- **Blocked at stock firmware downgrade validation.** The user selected the R2.15 `.img` and `.sig` in their separate upload controls, one after the other. The router enabled the final Update/Upgrade control. After the user clicked it, the UI displayed the exact error:

  ```text
  Firmware file is invalid or corrupted.
  ```

- No successful downgrade occurred. No OpenWrt `.trx` was flashed. No boot-bank switch was performed. No modified configuration was restored.
- The router was still on stock `R2.57` when work stopped.
- The user said they would shut everything down after approximately nine straight hours of work and take a break. There is no later confirmation in the retained record that power-off was completed.
- Known working connectivity at the stopping point: local Ethernet connectivity, ping to `192.168.29.1`, and access to the stock admin UI before shutdown.
- Known not working / not established:
  - Telnet on TCP/23 was closed at the time tested.
  - Root access was not obtained.
  - OpenWrt was not installed.
  - The R2.15 signing/validation compatibility with R2.57 remains unknown.
  - Recovery-bank and rollback claims have not been independently established.

## Core Breakthrough / Main Technical Findings

- The selected local firmware files were not found to be mismatched or obviously corrupt by file identity checks:
  - The two local R2.15 `.img` copies have identical SHA-256 hashes.
  - The two local R2.15 `.sig` copies have identical SHA-256 hashes.
  - The local OpenWrt `.trx` hash exactly matches the repository's published checksum entry recorded during the investigation.
- The R2.15 image contents identify the image as `JCOW414_R2.15` and contain a `HDR2` marker. The OpenWrt TRX also begins with `HDR2` and contains an OpenWrt build identifier and root-filesystem strings.
- This confirms **file identity / structural plausibility**, not vendor signature authenticity, acceptance by R2.57, or successful compatibility with this exact router.
- A decrypted stock configuration and a modified comparison configuration were available. The modified configuration's checksum did **not** match the computed MD5 value. Its first line differed from the original and contained an OS-command injection sequence described in the repository's root-unlocker approach. That technique is not reproduced as executable payload in this archive.
- The most important unresolved gate is the router's firmware validation decision: signing key, downgrade policy, format/profile checks, or another validation rule. The visible error does not distinguish among them.

## Evidence Labels Used in This Archive

- **[OBSERVED]** Directly observed in the session, actual mounted file, local network test, or exact UI error.
- **[HASH-VERIFIED]** Exact cryptographic digest computed on a mounted file.
- **[REPOSITORY CLAIM]** Stated by the GitHub project author; not independently tested on the user's router.
- **[INFERENCE]** Plausible explanation, not proven.
- **[UNKNOWN]** Not established by the evidence retained.
- **[NOT EXECUTED]** Discussed in docs or considered, but not performed on the router.

# 2. Artifacts, Repositories & File Architecture

## 2.1 GitHub Repository

- **Repository:** `Asjohn720/jiofiber-jcow414-openwrt`
- **URL:** https://github.com/Asjohn720/jiofiber-jcow414-openwrt
- **Purpose:** Unofficial OpenWrt 23.05 port/build and software-only installation guide for Sercomm JCOW414 / JCO4032-class JioFiber hardware, based on Airoha / Econet EN7528HU.
- **Repository metadata as observed during the session (time-sensitive historical snapshot):**
  - Created: `2026-10-15`.
  - Updated: `2026-11-05`.
  - A push/commit activity date of `2026-11-02` was noted.
  - Approximately 6 stars, 6 forks, and 11 open issues at inspection time.
  - Repository was described as very new (approximately one month old at inspection).
- **Important correction from user:** The user explicitly pointed to this exact new repository and noted that its author used the `.img` and `.sig` pair. The repo was treated as more directly relevant than older community reports alone. The user's correction was valid: old forum reports about firmware-key changes did not by themselves disprove the newer guide.

### Relevant repository documents / paths

The exact full repository tree was not preserved in the session record. The following paths/files were explicitly analyzed or referenced:

```text
jiofiber-jcow414-openwrt/
â”œâ”€â”€ README.md
â”œâ”€â”€ TESTING.md
â””â”€â”€ openwrt/
    â””â”€â”€ Build/
        â””â”€â”€ sha256sums
```

- `README.md` â€” main guide and installation flow.
- `TESTING.md` â€” maintainer's reported test results.
- `openwrt/Build/sha256sums` â€” checksum manifest containing the TRX hash.
- A Windows batch â€œroot unlockerâ€ script was included/referenced by the README and its source was inspected. **The exact path/name was not retained in the session record.**
- The actual build output filename recorded in the repo checksum manifest was:

  ```text
  openwrt-asjohn720-1.1-jcow414-econet-en7528-jiofiber_jcow414-squashfs-tclinux.trx
  ```

### README claims and installation flow (not executed)

1. Downgrade stock JCOW414 firmware to R2.15 using the vendor-format `.img` and `.sig` pair.
2. The guide describes a Windows batch-based configuration-backup modification that injects a root Telnet command into configuration content. The README claims the router executes injected commands before checksum validation, so a restore can report a checksum error even after command execution. This is an exploit-style configuration parser/restore behavior. The executable payload and reproduction steps are intentionally omitted here.
3. Install/flash the OpenWrt factory `.trx` image to the `tclinux` partition using a forced MTD write (`mtd -f` is referenced; the complete command line was not preserved in the record).
4. Change boot selection using the documented command below, then reboot:

   ```sh
   /usr/bin/sys bootflag swap
   ```

   This command is recorded because it appeared in the repository documentation. It was **not run** on the user's router.

5. The README says the OpenWrt UI is expected at `192.168.1.1` after boot.
6. The README claims AP setup is available with `br-lan` bridging all four LAN ports. Connect the main router's LAN to one JCOW414 LAN port. The target use case is AP/managed-switch operation.
7. The README states that GPON optical uplink functionality is not supported in this build; this is an AP-only use case, not a replacement optical WAN/ONT implementation.

### README dual-bank / rollback claims and inconsistency

- **[REPOSITORY CLAIM]** The device has two firmware banks:
  - Bank 1: `tclinux`, identified in the guide as MTD partition `mtd4`.
  - Bank 2: `tclinux_slave`, identified as MTD partition `mtd7`.
- **[REPOSITORY CLAIM]** The stock R2.15 firmware remains in Bank 2 and the device can automatically roll back if the new bank fails CRC/boot validation.
- **[OBSERVED IN DOC REVIEW]** The README's â€œzero-risk rollbackâ€ / dual-bank narrative was internally inconsistent: it asserted that the stock image remains in Bank 2, but the rollback instructions did not clearly show an explicit boot-flag command selecting Bank 2. The author also described automatic rollback on CRC failure.
- **[UNKNOWN]** Whether this particular R2.57 router has the described partition layout, whether Bank 2 contains recoverable stock firmware, and whether automatic rollback behaves as claimed.
- The guide's â€œzero-riskâ€ wording should not be treated as proof of zero risk.

### TESTING.md claims (maintainer-reported, not independently verified)

- All four LAN ports reportedly tested at 1 Gbps full duplex.
- 2.4 GHz Wi-Fi reportedly tested with MediaTek `MT7603E`.
- 5 GHz Wi-Fi reportedly tested with MediaTek `MT7613BE`.
- LuCI access and root SSH reportedly tested.
- USB 2.0 / USB 3.0 support reportedly tested.
- Configuration persistence reportedly tested.
- Throughput/speed testing was still pending.
- These are project-maintainer claims, not independent verification and not proof against the user's exact R2.57 hardware/firmware combination.

### Firmware checksum manifest entry

The exact recorded manifest entry was:

```text
43112eacecdcea64bb213520df50df18cbcd68fc4682932807e915e97883feb2 *openwrt-asjohn720-1.1-jcow414-econet-en7528-jiofiber_jcow414-squashfs-tclinux.trx
```

The uploaded local TRX has this exact SHA-256.

### External community context referenced

- Older community reports/discussions were said to suggest that firmware newer than approximately R2.49 may have changed the public signing key, causing normal R2.15 signature validation to fail.
- This was **not** established as fact for the user's exact R2.57 unit. The newer repository was presented as a counterexample/updated attempt, and the actual trust-key validation remained unresolved.
- No exact URL for the older community thread was preserved in the record; do not invent one.

## 2.2 Firmware and Configuration Files

All paths below are actual mounted paths in `/mnt/data` at archive creation. Hashes are SHA-256.

| Local file | Size (bytes) | SHA-256 | Findings / role |
|---|---:|---|---|
| `/mnt/data/SRCMTF1_JCOW414_R2.15.img` | 38,071,183 | `ad2977cca4b2796faa81cf0bf7d6f16b152fffdef1c73aba6b6dabc725bbca97` | R2.15 image copy 1; same hash as copy 2. |
| `/mnt/data/SRCMTF1_JCOW414_R2.15.sig` | 256 | `669961ce8d04cd0e0d14181b49469f87143f190c89ec11f57bac88e14384ea91` | Companion signature copy 1; same hash as copy 2. |
| `/mnt/data/SRCMTF1_JCOW414_R2.15(1).img` | 38,071,183 | `ad2977cca4b2796faa81cf0bf7d6f16b152fffdef1c73aba6b6dabc725bbca97` | Re-uploaded copy; byte-identical by SHA-256 to copy 1. |
| `/mnt/data/SRCMTF1_JCOW414_R2.15(1).sig` | 256 | `669961ce8d04cd0e0d14181b49469f87143f190c89ec11f57bac88e14384ea91` | Re-uploaded copy; byte-identical by SHA-256 to copy 1. |
| `/mnt/data/openwrt-jiofiber_jcow414_v1.1.trx` | 10,223,616 | `43112eacecdcea64bb213520df50df18cbcd68fc4682932807e915e97883feb2` | OpenWrt v1.1 TRX; hash exactly matches repo manifest entry. |
| `/mnt/data/RSVOTCXXXXXXXX_JCOW414.enc` | 154,528 | `1f97a7f55b7d7b94681c33c2099044a2f34e4d02045611f3205b648b5bff68dd` | Original encrypted router configuration backup. |
| `/mnt/data/RSVOTCXXXXXXXX_JCOW414.txt` | 154,507 | `3eb2287349aee6570f54824904d312a9416a43b597df5bc6dc38bccd44188b93` | Decrypted/plaintext representation of original configuration. |
| `/mnt/data/modified.txt` | 154,745 | `b7e5b546a19bf24b4890fdc5d943a89f5258508daeee3323f86c73fe5a48d0d7` | Modified plaintext comparison/configuration file. Do not restore. |
| `/mnt/data/modified_JCOW414.enc` | 154,768 | `559415c6a086bef53f87a29796de7fc594e3aa65a32bef9e6f4cb38274cb02d4` | Encrypted form of modified configuration. Do not restore. |
| `/mnt/data/Install_OpenSSL.bat` | 869 | Not recorded | Windows installer/environment helper for OpenSSL. Has a path-control-character defect; see below. |
| `/mnt/data/BackupRestore_819184b1_5f581da4.txt` | 2,971 | Not recorded | Saved HTML fragment for router backup/restore UI. Contains a session token in original source; token intentionally not copied here. |

### R2.15 IMG string/structure findings

- **[OBSERVED]** Image contains these strings/markers at the noted offsets:
  - Offset `0x1c`: `2.15`
  - Offset `0x34`: `Reliance`
  - Offset `0x74`: `Reliance_v2.15.img`
  - Offset `0x100`: `HDR2`
  - Offset `0x110`: `JCOW414_R2.15`
- This supports that the file is labelled for JCOW414 R2.15. It does not prove the router's currently installed bootloader/signature policy accepts it.

### Signature status

- The `.sig` file's size and SHA-256 were checked.
- **No cryptographic verification** was completed against a trusted Jio/Sercomm public key.
- A matching hash only proves that the local `.sig` bytes match the compared artifact/known hash. It does not establish who signed it or whether R2.57 trusts the signer.

### OpenWrt TRX structure findings

- First four bytes: `HDR2`.
- Build string at offset `0x10`: `OpenWrt-Asjohn720-r0-c4526c7`.
- Strings `rootfs` and `rootfs_data` found in the image.
- The repository README described the image as an OpenWrt 23.05 Airoha build for this hardware family.
- The hash match to repo manifest is strong file-integrity evidence, not a successful-boot guarantee.
- Repo README reportedly described a file size around 13.8 MB, while the uploaded local TRX is 10,223,616 bytes (about 10.22 MB decimal). Because its hash matches the manifest exactly, this size discrepancy alone does not mean the local file is corrupt. The README size statement may be approximate, refer to another representation, or be stale; exact cause not established.

## 2.3 Configuration Comparison / Checksum Findings

- The original config was decrypted into `RSVOTCXXXXXXXX_JCOW414.txt`.
- A modified plaintext file `modified.txt` was produced and compared against the original.
- **[OBSERVED]** The first line differed; the remaining 3,143 lines were reported identical to the original.
- The modified first line contained injected command logic intended to start Telnet, add a firewall allow rule, and set a root password. The exact line/payload and password are intentionally not included in this archive.
- `modified.txt`:
  - 154,745 bytes.
  - 3,144 lines.
  - LF line endings only.
  - SHA-256 `b7e5b546a19bf24b4890fdc5d943a89f5258508daeee3323f86c73fe5a48d0d7`.
- `modified_JCOW414.enc`:
  - 154,768 bytes.
  - SHA-256 `559415c6a086bef53f87a29796de7fc594e3aa65a32bef9e6f4cb38274cb02d4`.
  - Starts with OpenSSL salted-file marker `Salted__`.
- Checksum declaration at line 3012 of `modified.txt`:

  ```text
  config.checksum = "7d669de3e42ace6be9ee2286398e46ca"
  ```

- MD5 computed over the bytes before the checksum line (including the newline before that line):

  ```text
  1cf7898852d9b5b9303be87bcd6aff4f
  ```

- These values do not match. The modified config checksum was therefore considered invalid/unverified and must not be restored.
- The original configuration checksum was reported as verified during earlier analysis, but its checksum value / exact byte-range computation was not retained in the record.
- An experiment involving `modified_checksum0.txt` / `modified_checksum0_JCOW414.enc` was also mentioned. These temporary checksum-zero experiment artifacts are not present in the current mounted directory listing and their exact contents/results were not retained. Do not use them.
- A `key.txt` was referenced in earlier decryption work, but it is not present in the current mounted file listing and no key value is reproduced here. Treat it as sensitive.

## 2.4 Router Backup/Restore HTML Fragment

Local file: `/mnt/data/BackupRestore_819184b1_5f581da4.txt`.

The saved HTML source is a commented-out fragment of the stock backup/restore page. Relevant extracted details:

- Backup form name: `tf1_frmBackupSaveCurrentSettings`.
- Backup action: `?action=backup`.
- Backup UI warns that passwords and possibly sensitive information may be stored in cleartext in the encrypted configuration file and says to protect the file accordingly.
- Restore form name: `tf1_frmBackupRestoreSavedSettings`.
- Restore action: `platform.cgi`.
- Multipart upload field: `file.restore`.
- File input ID: `tf1_txtRestoreFile`.
- Accepted extension: `.enc`.
- Restore button name: `button.restore.statusPage`.
- JavaScript validation invocation in source: `check('tf1_txtRestoreFile', 'cfg', 1 ,'enc')`.
- A hidden form token appears in the original source. It is a session/security token and is redacted from this knowledge base.

Redacted structural excerpt (not a runnable reproduction; session token removed):

```html
<form name="tf1_frmBackupSaveCurrentSettings" method="post" action="?action=backup">
  <input type="hidden" name="thispage" id="thispage" value="factoryDefault.html">
  <!-- Save Current Settings button; warning about sensitive data in backup -->
</form>
<form name="tf1_frmBackupRestoreSavedSettings" id="tf1_frmBackupRestoreSavedSettings"
      action="platform.cgi" method="post" enctype="multipart/form-data">
  <input type="hidden" name="thispage" id="thispage" value="backupRestore.html">
  <input type="file" id="tf1_txtRestoreFile" name="file.restore" value="" accept=".enc">
  <input type="submit" name="button.restore.statusPage" value="Restore"
         onclick="return check('tf1_txtRestoreFile', 'cfg', 1 ,'enc')">
</form>
```

## 2.5 OpenSSL Installer Helper

Local file: `/mnt/data/Install_OpenSSL.bat`.

Original functional intent:

1. Install OpenSSL Light through Winget using package ID `ShiningLight.OpenSSL.Light`.
2. Add OpenSSL's install folder to the current command-shell `PATH`.
3. Confirm executable resolution and print version.

Commands contained in the file:

```bat
winget install --id ShiningLight.OpenSSL.Light --exact --source winget
where.exe openssl
openssl version
```

- **Important defect:** The actual PATH line in the file contains a backspace/control character (`0x08`) between `OpenSSL-Win64` and `in`, visually rendered as `OpenSSL-Win64<backspace>in`. It appears intended to be `C:\Program Files\OpenSSL-Win64\bin`, but the file as captured is not correct. This is an observation about the file's bytes, not a confirmed successful install.
- Exact original line represented safely:

  ```text
  set "PATH=%PATH%;C:\Program Files\OpenSSL-Win64\x08in"
  ```

- Do not assume OpenSSL was successfully installed or that this batch file ran without modification. The session notes do not preserve a successful Winget install result or OpenSSL version output.

## 2.6 Screenshots / Image Attachments

The following image files were mounted in the session. They were supplied as visual context during troubleshooting, but the retained conversation record does not attach a reliable description of every individual screenshot to its exact chronological action. They are therefore catalogued without guessing at their contents. Sizes and dimensions were read from the mounted files.

| Filename | Size (bytes) | Dimensions |
|---|---:|---:|
| `1000085132.jpg` | 308,821 | 1536Ã—1152 |
| `1000085133.jpg` | 300,133 | 1536Ã—1152 |
| `1000085223.jpg` | 296,936 | 1152Ã—1536 |
| `1794505904259.png` | 94,381 | 1920Ã—1080 |
| `b68f5a78-ee11-4de4-b26c-01dc19ca54e82887934239307850350.png` | 1,653,098 | 1536Ã—1152 |
| `image(20261112-213807).png` | 10,223 | 791Ã—116 |
| `image(20261112-214340).png` | 159,592 | 1920Ã—1080 |
| `image-1794496156354.jpg` | 318,092 | 1536Ã—1152 |
| `image-1794496168425.jpg` | 235,935 | 1536Ã—1152 |
| `image-1794496190905.jpg` | 226,245 | 1536Ã—1152 |
| `image-1794497176511.jpg` | 271,233 | 1536Ã—1152 |
| `image-1794497414592.jpg` | 272,803 | 1536Ã—1152 |
| `image-1794498486876.jpg` | 275,442 | 1536Ã—1152 |
| `image-1794499165880.jpg` | 321,261 | 1536Ã—1152 |
| `image-1794500352053.jpg` | 216,894 | 1536Ã—1152 |
| `image-1794503453946.jpg` | 233,230 | 1536Ã—1152 |
| `image-1794503678538.jpg` | 273,645 | 1152Ã—1536 |
| `image-1794504204011.jpg` | 301,385 | 1152Ã—1536 |
| `image-1794504400633.jpg` | 269,128 | 1152Ã—1536 |
| `image-1794504545793.jpg` | 265,146 | 1536Ã—1152 |
| `image-1794506137044.jpg` | 219,385 | 1152Ã—1536 |
| `image-1794506666869.jpg` | 222,785 | 1152Ã—1536 |
| `image-1794507051346.jpg` | 192,720 | 1536Ã—1152 |
| `image-1794510126699.jpg` | 415,755 | 1536Ã—1152 |
| `image-1794510252799.jpg` | 391,733 | 1152Ã—1536 |
| `image-1794510263024.jpg` | 175,289 | 1152Ã—1536 |
| `image-1794510274005.jpg` | 170,569 | 1152Ã—1536 |
| `image-1794510294596.jpg` | 177,104 | 1536Ã—1152 |
| `image-1794510407503.jpg` | 357,887 | 1536Ã—1152 |
| `image-1794511588276.jpg` | 201,241 | 1536Ã—1152 |
| `image-1794511865573.jpg` | 238,792 | 1536Ã—1152 |
| `image-1794512064296.jpg` | 371,648 | 1152Ã—1536 |
| `image-1794512643064.jpg` | 342,080 | 1152Ã—1536 |
| `image-1794512942396.jpg` | 271,978 | 1536Ã—1152 |
| `image-1794514351521.jpg` | 386,454 | 1536Ã—1152 |
| `image-1794515868224.jpg` | 295,909 | 1536Ã—1152 |
| `image-1794515946442.jpg` | 209,248 | 1536Ã—1152 |
| `image-1794517347930.jpg` | 270,502 | 1152Ã—1536 |

Total: **38 image files**. Their exact names and file metadata are preserved above; their per-image semantic interpretation is not recoverable from the retained notes.

# 3. Chronological Execution Log (A-to-Z)

> Chronology is reconstructed from retained notes and file timestamps. Exact timestamps for every turn/action were not preserved. Phases are ordered by the known flow, not by guessed minute-level timestamps.

### Phase 1: Define target and constraints

- **Action / Hypothesis:** Establish whether the user's own Sercomm JCOW414 can be converted to OpenWrt by software only, then repurposed as an AP.
- **Initial hardware/software facts:** JCOW414; hardware `0001`; stock firmware `R2.57`; admin `192.168.29.1`.
- **Constraints:** No UART/soldering. Isolated workbench network; Windows PC over Ethernet and router power only.
- **Outcome (`[PARTIAL]`):** Target and constraints established.
- **Root Cause / Technical Detail:** The repo's guide required first reaching R2.15, so the first gate was a software downgrade, not immediate flashing.

### Phase 2: Establish local connectivity

- **Action / Hypothesis:** Connect Windows PC directly to router and confirm the admin interface and IP reachability.
- **Observed values:** PC Ethernet `192.168.29.2`; router `192.168.29.1`.
- **Outcome (`[SUCCESS]`):** Ping to router worked; stock admin UI reachable.
- **Root Cause / Technical Detail:** Direct isolated LAN communication was functional. No WAN/ISP connection was needed for local management.

### Phase 3: Inspect Telnet availability

- **Action / Hypothesis:** Check whether the router already exposes Telnet for root access.
- **Outcome (`[FAILURE]`):** TCP port `23` was closed at time tested.
- **Root Cause / Technical Detail:** Telnet was not exposed by the stock state being tested. The test occurred **before** the modified configuration was restored; in fact, the modified config was never restored.
- **Important limitation:** Closed port 23 does not prove what an unexecuted configuration injection would do. It only records the pre-restore stock observation.

### Phase 4: Identify the new GitHub route

- **Action / Hypothesis:** Evaluate `https://github.com/Asjohn720/jiofiber-jcow414-openwrt` as a directly relevant and recent software-only installation guide.
- **User correction:** User emphasized that the repository was very new (about one month old) and the author used both `.img` and `.sig` files. Older reports should not be treated as conclusive against this newer guide.
- **Outcome (`[PARTIAL]`):** Repository identified as relevant. Its installation flow and claims were reviewed.
- **Root Cause / Technical Detail:** The repo's route depends on R2.15 acceptance, a config-restore root-unlocker technique, a TRX flash, and a boot-bank change. None of these later steps had yet been performed.

### Phase 5: Analyze repository installation approach

- **Action / Hypothesis:** Determine what the repo expects and whether its procedure plausibly matches the JCOW414.
- **Reviewed details:** README flow, TESTING.md, `openwrt/Build/sha256sums`, root-unlocker batch script source, dual-bank claims, AP mode claims.
- **Outcome (`[PARTIAL]`):** Repository contents were found internally plausible but included unverified maintainer claims and a dual-bank/rollback documentation inconsistency.
- **Root Cause / Technical Detail:** README describes R2.15 downgrade first; config-backup command injection; forced MTD write to `tclinux`; `/usr/bin/sys bootflag swap`; LuCI at `192.168.1.1`. Repo says AP mode only; GPON optical uplink unsupported.
- **Safety/operational boundary:** The root-unlocker is an exploit-style config injection. Exact payload and step-by-step exploitation procedure are not reproduced in this archive.

### Phase 6: Collect and decrypt router configuration backup

- **Action / Hypothesis:** Inspect the router's configuration format and identify useful configuration fields/possible management settings.
- **Artifacts:**
  - `RSVOTCXXXXXXXX_JCOW414.enc` â€” encrypted backup.
  - `RSVOTCXXXXXXXX_JCOW414.txt` â€” decrypted/plaintext config.
  - A `key.txt` was referenced in earlier work; it is not currently in the mounted artifact inventory.
  - `BackupRestore_819184b1_5f581da4.txt` â€” HTML snippet from backup/restore page.
  - `Install_OpenSSL.bat` â€” OpenSSL installation helper.
- **Outcome (`[PARTIAL]`):** Original config plaintext became available and was used for a comparison. The decryption command/key derivation details were not preserved in retained notes.
- **Root Cause / Technical Detail:** Router backup UI accepts `.enc` on restore field `file.restore`; source warns that potentially sensitive values may be stored in the encrypted file. The encrypted config's content is not necessarily safe to share.

### Phase 7: Create and compare modified configuration

- **Action / Hypothesis:** Compare original config with a modified version designed in the prior session to enable Telnet/root access as described by the repo's approach.
- **Observed details:**
  - `modified.txt` has 3,144 lines and 154,745 bytes.
  - Only first line differed from the original; the other 3,143 lines were reported identical.
  - First line contained a command-injection sequence intended to start Telnet, open a firewall path, and set a root password.
  - `modified_JCOW414.enc` begins with OpenSSL `Salted__` marker.
- **Outcome (`[FAILURE]` for validation; `[PARTIAL]` for reverse engineering):** The modified config checksum calculation did not match the declared checksum.
- **Exact checksum details:**

  ```text
  Declared: 7d669de3e42ace6be9ee2286398e46ca
  Computed: 1cf7898852d9b5b9303be87bcd6aff4f
  Algorithm: MD5
  Input: bytes before checksum line, including preceding newline
  Checksum declaration location: line 3012
  ```

- **Root Cause / Technical Detail:** The modified configuration's checksum could not be validated. It was explicitly not safe to restore. No router restore was performed.
- **Credential handling:** The modified line included a root password value that was exposed during prior tool output. Do not reuse that password. Its literal value is intentionally not repeated.
- **Additional experiment:** `modified_checksum0.txt` / `modified_checksum0_JCOW414.enc` zero-checksum experiment artifacts were mentioned but not preserved in current directory. Exact results unavailable.

### Phase 8: Inspect firmware files

- **Action / Hypothesis:** Verify the exact R2.15 firmware pair and OpenWrt TRX before any upload.
- **Outcome (`[SUCCESS]` for file identity checks; `[PARTIAL]` for authenticity/compatibility):** Files were inspected and hashed.
- **R2.15 image findings:** `2.15`, `Reliance`, `Reliance_v2.15.img`, `HDR2`, `JCOW414_R2.15` strings at offsets documented in Section 2.
- **TRX findings:** `HDR2` header; `OpenWrt-Asjohn720-r0-c4526c7`; `rootfs` and `rootfs_data`; SHA-256 exactly matches repo manifest.
- **Signature findings:** `.sig` size 256 bytes and hash recorded. No verification against trusted Jio/Sercomm public key was completed.
- **Outcome:** No wrong-model marker or hash mismatch was found in the uploaded files. That is not a guarantee that R2.57 accepts them.

### Phase 9: Confirm exact files and user requests certainty

- **Action / Hypothesis:** Re-check the three files after user uploaded them again and asked for certainty and speed.
- **User wording/intent:** Asked to go through it â€œ100% sureâ€ and keep it quick; user was frustrated by extended back-and-forth and approximately 8.5 hours of work.
- **Outcome (`[SUCCESS]`):** Re-uploaded `.img`, `.sig`, and `.trx` had same hashes as the previously checked files. Re-upload did not reveal any mismatch.
- **Limitation repeated:** Cannot claim 100% certainty on signature authenticity, R2.57 downgrade acceptance, or bank recovery because evidence does not establish those facts.

### Phase 10: Attempt R2.15 downgrade via stock UI

- **Action / Hypothesis:** Follow repository Step 1 and use separate firmware UI fields for `.img` and `.sig`.
- **User-reported sequence:** Both files were selected and uploaded one by one. The final Update/Upgrade button became clickable. User clicked it.
- **Outcome (`[FAILURE]`):** Exact UI error:

  ```text
  Firmware file is invalid or corrupted.
  ```

- **Root Cause / Technical Detail:** Router rejected the firmware package during validation. This does **not** by itself prove the image bytes are corrupt.
- **Possible causes (not distinguished by error):**
  - Signature/public-key mismatch.
  - Downgrade blocked by version policy.
  - Firmware profile/header/format incompatibility.
  - Another vendor validation rule.
- **Important user clarification:** User confirmed both `.img` and `.sig` were selected through their separate fields before clicking Update. Therefore, the error cannot be attributed simply to uploading only the `.img`.
- **Outcome:** No downgrade occurred. User was advised not to force the upgrade or keep retrying identical files.

### Phase 11: Consolidate state and recommend pause

- **Action / Hypothesis:** Stop repeated blind attempts and list what exists, what is missing, and what can safely be investigated next.
- **Outcome (`[PARTIAL]`):** State reset into four groups: known artifacts, failure at firmware validation, configuration evidence, unresolved compatibility questions.
- **Recommended order:** Analyze original/modified config evidence; establish the actual R2.57 validation cause; compare repository claims with exact hardware/firmware; only then decide viability.
- **User update:** User stated they had spent nine straight hours and needed a break, and would shut everything down.
- **Outcome (`[PAUSED]`):** No additional router operations were attempted. Last known firmware remains stock R2.57. Power-off intent was stated, completion not confirmed.

### Phase 12: Request for archival knowledge base

- **Action / Hypothesis:** User requested a comprehensive chronological Markdown archive for human reading and local LLM ingestion, specifying exact headings and zero omission of technical details.
- **Outcome (`[IN PROGRESS]`):** This file was produced from retained conversation notes and mounted files. It flags missing transcript details rather than fabricating them. Secret tokens, passwords, keys, and executable exploit payload details are redacted.

# 4. Blockers, Loopholes & Breakthroughs

## 4.1 Main Deadlock: R2.57 Rejects R2.15 Package

- Local file integrity checks passed for the R2.15 IMG/SIG pair; the two copies of each artifact hash identically.
- The repo says this `.img` + `.sig` pair is the correct downgrade path.
- The UI accepted both files into their separate fields sufficiently to enable the final Update/Upgrade button.
- The actual upgrade request failed with â€œFirmware file is invalid or corrupted.â€
- The visible error is generic. It does not identify the internal rejection reason.
- **Leading hypothesis:** R2.57 may enforce a signing key or downgrade policy that prevents acceptance of R2.15. This remains a hypothesis, not a confirmed cause.
- Older community observations about a key change after approximately R2.49 were noted, but the newer repository may have different evidence/approach. No trusted-key cryptographic test was completed.
- Repeatedly uploading the same files will not provide new diagnostic information unless an input changes or a more specific validation log becomes available.

## 4.2 Configuration / Root-Unlocker Technique

- The repo describes a configuration restore weakness where a crafted configuration line is interpreted as executable OS commands before the checksum failure is enforced.
- The prior work created a modified config whose first line attempted to start Telnet, allow access through the firewall, and set a root password.
- A plaintext-vs-original comparison showed only the first line differed; all other 3,143 lines were reported identical.
- The modified checksum did not match the MD5 computed over the expected bytes.
- **Critical state:** This file was never restored. Telnet port 23 was observed closed before any such restore.
- The precise executable payload, password, and exact reproduction steps are intentionally omitted from this archive. This preserves the technical conclusion without producing a ready-to-run configuration-injection exploit.
- The existence of the technique in the repository does not prove that it works on R2.57 or the user's exact hardware/firmware build.

## 4.3 Decryption and Format Findings

- Original encrypted config and plaintext counterpart exist in mounted data.
- Modified encrypted config begins with `Salted__`, consistent with an OpenSSL salted-format envelope.
- A `key.txt` was referenced earlier; its contents are not included here.
- The exact OpenSSL decrypt/encrypt command, cipher, key derivation options, and key value were not preserved in retained notes. **Do not infer them from `Salted__` alone.**
- The `Install_OpenSSL.bat` helper contains a malformed PATH line with byte `0x08` in the presumed `bin` path.
- Original backup checksum had reportedly been verified, but the exact checksum and calculation were not retained.

## 4.4 OpenWrt Hardware Support and Dual-Bank Risk

- Repo claims an OpenWrt 23.05 build for Airoha/Econet EN7528HU and JCOW414.
- The uploaded TRX hash exactly matches the repo manifest and contains plausible OpenWrt markers.
- Maintainer says LAN ports, Wi-Fi chipsets, LuCI, root SSH, USB, and persistence were tested.
- Throughput testing was reportedly pending.
- The repo states GPON optical uplink unsupported, meaning AP-only utility.
- Dual-bank partition names and offsets were repository claims, not inspected on the user's router.
- The README's zero-risk rollback wording is not sufficiently supported; the documented rollback narrative has an ambiguity regarding explicit selection of Bank 2.
- No MTD write, bootflag operation, or reboot into OpenWrt happened.

## 4.5 What Is Actually Established vs Not

| Claim | Evidence level | Status |
|---|---|---|
| Router is Sercomm JCOW414 HW 0001, R2.57 | User-provided / device context | Established for this session |
| PC `192.168.29.2` can ping router `192.168.29.1` | Direct test | Established |
| TCP/23 closed before modified config restore | Direct test | Established |
| R2.15 IMG identifies JCOW414_R2.15 | Binary strings/offset inspection | Established |
| R2.15 IMG/SIG copies are identical by SHA-256 | Direct hash computation | Established |
| TRX hash matches repo manifest | Direct hash comparison | Established |
| `.sig` cryptographically trusted by Jio/Sercomm | No signature verification | Unknown |
| R2.57 rejects due to changed key | Generic error + historical reports | Hypothesis only |
| R2.57 refuses downgrade independent of signature | Not tested separately | Unknown |
| Modified config can trigger shell commands on R2.57 | README claim / local crafted file not restored | Unknown |
| Config checksum invalid | MD5 mismatch for modified text | Established |
| OpenWrt will boot on this specific device | Maintainer claims and image inspection only | Not proven |
| Bank 2 retains stock recoverable image | README claim only | Not proven |
| OpenWrt supports AP mode | README and TESTING.md claim | Reported, not independent |
| GPON WAN supported | README says no | Unsupported according to repo |

# 5. Master Code & Command Vault

## 5.1 Known-safe local network values (observed)

```text
Router model:       Sercomm JCOW414
Hardware version:   0001
Stock firmware:     R2.57
Router admin IP:    192.168.29.1
Windows PC IP:      192.168.29.2
OpenWrt expected UI IP (repo claim): 192.168.1.1
Telnet TCP port:    23 (closed during pre-restore test)
```

## 5.2 Known repository command reference (not executed)

```sh
/usr/bin/sys bootflag swap
```

- Repository says to use this to switch boot selection after flashing.
- Not executed on user's router.
- Not a recommendation to run without verifying the correct partition layout and recovery procedure for the exact device.

## 5.3 Repository flash references (incomplete; do not execute from this archive)

```text
Target partition named by repo: tclinux
Repo-reported partition mapping: tclinux = mtd4; tclinux_slave = mtd7
Repo mentions forced MTD write flag: mtd -f
```

- The complete MTD write command was not preserved in the retained record and is intentionally not reconstructed.
- No MTD command was run.

## 5.4 OpenSSL helper commands (copied from local BAT)

```bat
winget install --id ShiningLight.OpenSSL.Light --exact --source winget
where.exe openssl
openssl version
```

- File: `/mnt/data/Install_OpenSSL.bat`.
- The PATH line has a `0x08` control character where `\b` would normally be expected. Do not rely on the helper unchanged.
- No successful OpenSSL installation/version output was preserved.

## 5.5 Router backup/restore field names (structural reference)

```text
Backup form:        tf1_frmBackupSaveCurrentSettings
Backup action:      ?action=backup
Restore form:       tf1_frmBackupRestoreSavedSettings
Restore action:     platform.cgi
Restore file field: file.restore
Restore file ID:    tf1_txtRestoreFile
Accepted extension: .enc
Restore button:     button.restore.statusPage
Page marker:        backupRestore.html
Validation call:    check('tf1_txtRestoreFile', 'cfg', 1 ,'enc')
```

- Original HTML fragment contains a hidden session token: redacted.
- The UI source warns that passwords and other sensitive information may be present in the encrypted configuration backup.

## 5.6 Verified artifact hashes

```text
R2.15 IMG:
ad2977cca4b2796faa81cf0bf7d6f16b152fffdef1c73aba6b6dabc725bbca97

R2.15 SIG:
669961ce8d04cd0e0d14181b49469f87143f190c89ec11f57bac88e14384ea91

OpenWrt TRX:
43112eacecdcea64bb213520df50df18cbcd68fc4682932807e915e97883feb2

Original encrypted config:
1f97a7f55b7d7b94681c33c2099044a2f34e4d02045611f3205b648b5bff68dd

Original plaintext config:
3eb2287349aee6570f54824904d312a9416a43b597df5bc6dc38bccd44188b93

Modified plaintext config:
b7e5b546a19bf24b4890fdc5d943a89f5258508daeee3323f86c73fe5a48d0d7

Modified encrypted config:
559415c6a086bef53f87a29796de7fc594e3aa65a32bef9e6f4cb38274cb02d4
```

## 5.7 Checksum discrepancy reference

```text
config.checksum declared:
7d669de3e42ace6be9ee2286398e46ca

MD5 computed over bytes before checksum declaration, including preceding newline:
1cf7898852d9b5b9303be87bcd6aff4f

Result:
MISMATCH â€” modified configuration is not validated; do not restore.
```

## 5.8 Intentionally withheld executable material

- Exact root-unlocker command-injection line/payload.
- Exact modified root password value.
- Encryption/decryption key value (`key.txt` was referenced).
- Hidden session token from the original backup/restore HTML.
- Any executable config-restore bypass or signature-bypass procedure.
- Complete MTD flash command, which was not preserved in the retained record.

These were not omitted accidentally. The retained record either did not provide complete exact values or the details are sensitive/security-critical and should not be repackaged as a ready-to-run exploit/flash recipe.

# 6. Next Steps & Open Threads

## 6.1 Immediate Next Action

**Do not attempt another upgrade, restore, flash, or boot-bank operation immediately.** The previous session ended deliberately after approximately nine hours of troubleshooting. Preserve the current stock state.

When resuming, the next useful task is a read-only evidence pass that answers this question:

> Why does stock firmware R2.57 reject the exact, hash-verified R2.15 `.img` + `.sig` pair?

Prioritize distinguishing:

1. Signature verification failure / signer key not trusted.
2. Firmware downgrade/version policy rejection.
3. Image header, hardware profile, model, or region mismatch.
4. Another stock-firmware validation requirement.

No current evidence distinguishes these cases. Do not label one as the root cause until validation evidence supports it.

## 6.2 Recommended Investigation Order

1. **Preserve existing files unchanged.** Keep original `.enc`, plaintext backup, R2.15 pair, and OpenWrt TRX. Do not overwrite originals with experiments.
2. **Verify the downloaded signature through an independently trusted public key/source if one exists.** The local hash is not a signature verification.
3. **Review the repository's current README, TESTING.md, commit history, issues, and checksum manifest** for any explicit R2.57 test evidence. Distinguish maintainer confirmation from user reports and code inspection.
4. **Investigate stock firmware validation behavior without submitting modified images.** Prefer logs, documented validation output, or non-destructive inspection over trial-and-error uploads.
5. **Treat config restore as a separate unresolved path.** The modified config currently has a checksum mismatch and must not be restored. Reconstruct only from the unmodified original and verified format information; do not assume the repo's injection behavior works on R2.57.
6. **Before any future OpenWrt flash, independently establish recovery feasibility.** Do not rely on â€œzero-riskâ€ language. Validate exact partition mapping and which bank holds the stock image for this specific device/firmware revision.
7. **If and only if OpenWrt is safely installed**, configure LAN bridge/AP mode as documented, accounting for expected `br-lan`, all four LAN ports, and no GPON support.

## 6.3 Unresolved Questions / Edge Cases

- Does R2.57 trust the public key corresponding to the supplied R2.15 `.sig`?
- What exact internal validation check produced â€œFirmware file is invalid or corrupted.â€?
- Does the stock admin page require a different pairing/order/content encoding than the two separate file controls as used? User did upload both separately and the final button became active, so simple omission is ruled out.
- Does R2.57 enforce anti-rollback independent of signature?
- Is the R2.15 IMG a valid package for this unit's region/operator/hardware revision, not merely labelled JCOW414?
- What are the exact encryption cipher, key derivation parameters, and key source for `.enc`? The retained notes do not include the decryption command.
- What is the exact original checksum algorithm/input range and checksum value? Earlier analysis reported it verified but details were lost.
- Can the modified configuration's checksum be made valid through legitimate format handling? Current modified checksum mismatches; no restore was performed.
- Does a config restore vulnerability exist on R2.57 or only on an older firmware revision?
- Are all four LAN ports, both Wi-Fi radios, LuCI, SSH, USB, and persistence reproducible on this exact hardware revision? Repo tests are maintainer reports.
- Is throughput acceptable? Repo's TESTING.md reportedly said throughput testing was still pending.
- Does the actual device have the reported dual-bank layout (`mtd4` / `mtd7`)? Not inspected.
- Is the backup in Bank 2 stock and recoverable? Not established.
- Does automatic CRC/boot rollback work? Not established.
- Why does README size (~13.8 MB) differ from local TRX size (10,223,616 bytes) despite the exact manifest hash match? Cause unknown; likely stale/approximate documentation or different size convention, but not proven.
- The local `Install_OpenSSL.bat` contains a `0x08` control byte in the PATH path; determine whether the script was modified/transport-corrupted before reuse.
- The exact chronological mapping and semantic contents of the 39 screenshot files were not preserved in notes. Filenames and dimensions are catalogued in Section 2.6, but per-image interpretation remains an archive gap.
- The exact older community thread URL about possible post-R2.49 key changes was not preserved.
- The full original chat transcript, including exact wording and timestamps of every turn, is unavailable in the retained context. This document is a high-detail reconstruction, not a byte-for-byte transcript.

## 6.4 Resume-State Checklist

- [ ] Confirm router is powered off or still isolated before reconnecting.
- [ ] Confirm model `JCOW414`, hardware `0001`.
- [ ] Confirm stock firmware still `R2.57`.
- [ ] Keep PC/router on isolated Ethernet; known settings were PC `192.168.29.2`, router `192.168.29.1`.
- [ ] Do not restore `modified_JCOW414.enc`.
- [ ] Do not upload the same R2.15 pair again without new diagnostic evidence.
- [ ] Do not flash the TRX or run `sys bootflag swap` until recovery/partition assumptions are verified.
- [ ] Keep a copy of the original encrypted backup and its decrypted plaintext unchanged.
- [ ] Treat any previously exposed modified-config password as compromised; do not reuse it.

---

# Archive Integrity / Limitations

- This knowledge base includes all technical findings and artifact metadata retained in the current conversation context and mounted filesystem at creation time.
- It is not a literal export of the full chat transcript. Exact per-message timestamps, some original phrasing, the exact decryption command/key derivation, exact root-unlocker payload, original root password, hidden page token, and complete flash command were not preserved or are intentionally redacted.
- The screenshots were catalogued, but the retained session record did not preserve a reliable one-to-one map between every screenshot and each troubleshooting turn.
- The exact local file hashes in Section 2.2 were recomputed in the active environment at archive creation. No file was modified by this archive-generation operation.
- No router operation was performed while generating this archive.

