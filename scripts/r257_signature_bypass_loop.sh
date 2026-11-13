#!/bin/sh
# ==============================================================================
# Sercomm JCOW414 R2.57 Firmware Signature Verification Bypass Loop
# Author / Credit: itsyourap / JFC-Group Community
# Purpose:
#   When downgrading from R2.57 to R2.15 via the Web UI, the Sercomm firmware
#   upgrade daemon validates the firmware package and outputs rejection errors
#   into a temporary status file: /tmp/firmCheckRes.txt.
#
#   When this status file contains error codes, the Web UI rejects the upload with:
#       "Firmware file is invalid or corrupted."
#
#   By running this continuous loop in an active root shell prior to clicking
#   "Upgrade" in the Web UI, the verification error file is immediately cleared
#   whenever it is created, tricking the upgrade CGI handler into treating the
#   signature check as successful.
#
# Usage (requires root shell / Telnet / UART):
#   1. chmod +x r257_signature_bypass_loop.sh
#   2. ./r257_signature_bypass_loop.sh &
#   3. Navigate to http://192.168.29.1/ -> Maintenance -> Firmware Upgrade
#   4. Select SRCMTF1_JCOW414_R2.15.img and SRCMTF1_JCOW414_R2.15.sig
#   5. Click Upgrade while the script is actively looping in background
# ==============================================================================

echo "[*] Starting JCOW414 firmware signature bypass loop..."
echo "[*] Monitoring /tmp/firmCheckRes.txt (Press Ctrl+C to stop)..."

while true; do
    if [ -e /tmp/firmCheckRes.txt ]; then
        # Force overwrite the check result to return success / empty
        cat /dev/null > /tmp/firmCheckRes.txt
        echo "[+] Intercepted /tmp/firmCheckRes.txt -> Overwritten with success!"
    fi
    # Minimal sleep to prevent 100% CPU starvation while keeping latency low
    usleep 10000 2>/dev/null || sleep 0.01 2>/dev/null || true
done
