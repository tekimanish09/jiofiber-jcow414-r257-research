#!/usr/bin/env python3
"""
JioFiber Sercomm JCOW414 Configuration Checksum Calculator & Updater
Author: Community Research Archive
Description:
    Computes and optionally updates the MD5 checksum embedded in decrypted
    JioFiber Sercomm JCOW414 router configuration files.
    
    The router firmware calculates the MD5 digest over all bytes from the
    beginning of the file up to immediately before the line declaring:
        config.checksum = "..."
"""

import sys
import os
import hashlib
import argparse

CHECKSUM_MARKER = b'config.checksum = "'

def calculate_checksum(file_path):
    if not os.path.isfile(file_path):
        print(f"[-] Error: File '{file_path}' not found.")
        return None, None, None

    with open(file_path, "rb") as f:
        data = f.read()

    idx = data.find(CHECKSUM_MARKER)
    if idx == -1:
        print("[-] Error: 'config.checksum' marker not found in file.")
        return None, None, None

    # Bytes prior to the marker (includes the preceding newline)
    pre_checksum_bytes = data[:idx]

    # Compute MD5
    md5_hash = hashlib.md5(pre_checksum_bytes).hexdigest()

    # Extract declared checksum
    end_quote = data.find(b'"', idx + len(CHECKSUM_MARKER))
    if end_quote != -1:
        declared_checksum = data[idx + len(CHECKSUM_MARKER):end_quote].decode("ascii", errors="ignore")
    else:
        declared_checksum = "UNKNOWN"

    return md5_hash, declared_checksum, idx

def main():
    parser = argparse.ArgumentParser(description="Verify or update JioFiber Sercomm config checksum")
    parser.add_argument("config_file", help="Path to decrypted config file (.txt)")
    parser.add_argument("--update", action="store_true", help="Update the config file with the computed checksum")
    args = parser.parse_args()

    computed, declared, idx = calculate_checksum(args.config_file)
    if not computed:
        sys.exit(1)

    print(f"[*] Analyzing file: {args.config_file}")
    print(f"[*] Checksum line offset: {idx} bytes")
    print(f"[*] Declared Checksum:    {declared}")
    print(f"[*] Computed MD5 Hash:    {computed}")

    if computed.lower() == declared.lower():
        print("[+] STATUS: VALID! The declared checksum matches the computed digest.")
    else:
        print("[-] STATUS: MISMATCH! The declared checksum is invalid.")
        if args.update:
            with open(args.config_file, "rb") as f:
                content = f.read()
            
            old_line = f'config.checksum = "{declared}"'.encode("utf-8")
            new_line = f'config.checksum = "{computed}"'.encode("utf-8")
            
            if old_line in content:
                updated_content = content.replace(old_line, new_line, 1)
                with open(args.config_file, "wb") as f:
                    f.write(updated_content)
                print(f"[+] Updated '{args.config_file}' with valid checksum: {computed}")
            else:
                print("[-] Could not replace checksum string reliably.")

if __name__ == "__main__":
    main()
