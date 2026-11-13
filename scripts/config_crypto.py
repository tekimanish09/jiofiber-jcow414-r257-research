#!/usr/bin/env python3
"""
JioFiber Sercomm JCOW414 Configuration Encryption / Decryption Helper
Author: Community Research Archive
Description:
    Demonstrates the exact OpenSSL cryptographic envelope used by JioFiber
    Sercomm JCOW414 routers to encrypt/decrypt configuration backups (.enc files).
    
    Technical Details:
    - Cipher: AES-128-CBC
    - Message Digest for Key Derivation: SHA-256 (-md sha256)
    - Envelope: Standard OpenSSL salted binary header ("Salted__" + 8-byte salt)
    
    Equivalent OpenSSL CLI Commands:
    Decrypt:
        openssl aes-128-cbc -d -pass pass:<KEY> -in backup.enc -out config.txt -md sha256
    Encrypt:
        openssl aes-128-cbc -e -pass pass:<KEY> -in config.txt -out backup.enc -md sha256
"""

import sys
import os
import subprocess
import argparse

def find_openssl():
    # Common locations on Windows and Linux
    candidates = [
        "openssl",
        "C:\\Program Files\\OpenSSL-Win64\\bin\\openssl.exe",
        "C:\\Program Files (x86)\\OpenSSL-Win32\\bin\\openssl.exe",
        "C:\\Program Files\\Git\\usr\\bin\\openssl.exe",
        "/usr/bin/openssl",
        "/usr/local/bin/openssl"
    ]
    for c in candidates:
        try:
            res = subprocess.run([c, "version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if res.returncode == 0:
                return c
        except Exception:
            continue
    return None

def decrypt(openssl_bin, enc_file, out_file, key):
    cmd = [
        openssl_bin, "aes-128-cbc", "-d",
        "-pass", f"pass:{key}",
        "-in", enc_file,
        "-out", out_file,
        "-md", "sha256"
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if res.returncode == 0:
        print(f"[+] Successfully decrypted '{enc_file}' -> '{out_file}'")
        return True
    else:
        print(f"[-] Decryption failed: {res.stderr.decode('utf-8', errors='ignore').strip()}")
        return False

def encrypt(openssl_bin, txt_file, out_file, key):
    cmd = [
        openssl_bin, "aes-128-cbc", "-e",
        "-pass", f"pass:{key}",
        "-in", txt_file,
        "-out", out_file,
        "-md", "sha256"
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if res.returncode == 0:
        print(f"[+] Successfully encrypted '{txt_file}' -> '{out_file}'")
        return True
    else:
        print(f"[-] Encryption failed: {res.stderr.decode('utf-8', errors='ignore').strip()}")
        return False

def main():
    parser = argparse.ArgumentParser(description="JCOW414 Config Encrypt/Decrypt Utility")
    parser.add_argument("action", choices=["encrypt", "decrypt"], help="Action to perform")
    parser.add_argument("-i", "--input", required=True, help="Input file path")
    parser.add_argument("-o", "--output", required=True, help="Output file path")
    parser.add_argument("-k", "--key", required=True, help="Passphrase encryption key")
    args = parser.parse_args()

    openssl_bin = find_openssl()
    if not openssl_bin:
        print("[-] Error: OpenSSL binary not found in PATH or standard system directories.")
        sys.exit(1)

    print(f"[*] Using OpenSSL: {openssl_bin}")
    if args.action == "decrypt":
        decrypt(openssl_bin, args.input, args.output, args.key)
    elif args.action == "encrypt":
        encrypt(openssl_bin, args.input, args.output, args.key)

if __name__ == "__main__":
    main()
