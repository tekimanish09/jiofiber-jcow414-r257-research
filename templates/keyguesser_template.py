#!/usr/bin/env python3
"""
JioFiber Sercomm Configuration Encryption Key Guesser (Template)
Based on research by itsyourap (https://github.com/JFC-Group/JF-Customisation)
Purpose:
    Derives the AES-128-CBC key used to encrypt the router configuration backup (.enc)
    for Sercomm JCOW414 routers (works across firmwares like R2.15, R2.49, R2.57).

Instructions:
    1. Fill in ROUTER_SERIAL and ROUTER_SSID from the sticker on your router.
    2. Place your downloaded .enc backup in the same directory.
    3. Run: python keyguesser_template.py
"""

from itertools import permutations
import subprocess
import os
import sys

# ==============================================================================
# USER CONFIGURATION (Fill with your router's sticker details)
# ==============================================================================
ROUTER_SERIAL = "[YOUR_ROUTER_SERIAL]"       # e.g. "RSVOTCXXXXXXXX" (on router sticker)
ROUTER_SSID   = "[YOUR_DEFAULT_SSID_SUFFIX]" # Suffix of default SSID (e.g. if SSID is "JioFiber-XXXXX", use "XXXXX")
ENC_FILENAME  = "backup.enc"                  # Name of your encrypted config file
OUT_FILENAME  = "config_decrypted.txt"        # Output file if decryption succeeds
# ==============================================================================

# Known Sercomm vendor salt / key strings across JioFiber firmwares
KEY_STRINGS = [
    "1n0NaZQnC9oxcfwf", "us4AQiJAgbj0Fmxq", "NTqK8Ps5iFke8zrp", "bfqerloC15y79WQZ",
    "9gNzEbuDjtyT9Pyc", "uuphsZuO92AZW5GJ", "qdySWmmvYKdBcO53", "Q7ODauKsxUAUtbR7",
    "Kohgiem4joochei3", "6f1D27JyLm70GUUu", "zuFbKywMhJjVEhk3", "6uMrt5ricsD1ABDh",
    "iPjZ8bYm6s3uGYVf", "QGwaPHx2K1rNDTmL", "fJ7OeRF2TvqKdR30"
]

def try_decrypt(key):
    # Modern firmwares / OpenSSL use -md sha256 with the passphrase directly
    cmd = [
        "openssl", "aes-128-cbc", "-d",
        "-pass", f"pass:{key}",
        "-in", ENC_FILENAME,
        "-out", OUT_FILENAME,
        "-md", "sha256"
    ]
    p = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    _, _ = p.communicate()
    if p.returncode == 0:
        print(f"\n[+] SUCCESS! Decryption Key found: {key}")
        print(f"[+] Decrypted configuration saved to: {OUT_FILENAME}")
        sys.exit(0)

def main():
    if not os.path.isfile(ENC_FILENAME):
        print(f"[-] Encrypted file '{ENC_FILENAME}' not found.")
        sys.exit(1)

    print(f"[*] Starting key derivation for Serial: {ROUTER_SERIAL}, SSID Suffix: {ROUTER_SSID}")
    
    for idx, key_str in enumerate(KEY_STRINGS):
        components = [ROUTER_SERIAL, key_str, ROUTER_SSID]
        perms = []
        for i in range(1, len(components) + 1):
            for c in permutations(components, i):
                perms.append("".join(c))

        for candidate in perms:
            try_decrypt(candidate)

    print("[-] Key search finished. None of the standard combinations succeeded.")

if __name__ == "__main__":
    main()
