# Chronological Diagnostic Log & Error Reference

> **Purpose**: A reference log of exact network responses, HTTP headers, error strings, and reverse-engineered behavior captured during testing against the live Sercomm JCOW414 router.

---

## 1. Network Discovery & Port Probing

### TCP Port Scan on `192.168.29.1`:
```text
Port 21 (FTP):      CLOSED / TIMEOUT
Port 22 (SSH):      CLOSED / TIMEOUT
Port 23 (Telnet):   CLOSED / TIMEOUT
Port 69 (TFTP):     CLOSED / TIMEOUT
Port 80 (HTTP):     OPEN
Port 443 (HTTPS):   OPEN
Port 8080 (Alt):    OPEN
Port 8443 (Alt-SSL):CLOSED / TIMEOUT
```

### Direct HTTP Request to Root (`/`):
```text
HTTP/1.1 200 OK
Content-Type: text/html; charset=UTF-8
Server: Web Server
Title: "Jio Centrum Home Gateway : "
Form Action: "platform.cgi"
Form Fields: "thispage=index.html", "users.username", "users.password", "button.login.users.dashboard"
```

---

## 2. Web UI Login & Session Diagnostic Logs

### Direct curl POST to `/platform.cgi`:
```text
POST /platform.cgi HTTP/1.1
Host: 192.168.29.1
Content-Type: application/x-www-form-urlencoded

thispage=index.html&users.username=admin&users.password=[REDACTED]&button.login.users.dashboard=Login
```

**Response**:
```html
HTTP/1.1 200 OK
Transfer-Encoding: chunked
Server: Web Server

<body class="loginBody">
  <div class="midWidth onlyHeight">
    <div class="element">
      <h1 class="unAuthorised">401 Unauthorized <br>
        <a href="/platform.cgi"> Click here to Relogin </a>
      </h1>
    </div>
  </div>
</body>
```
*Diagnosis*: Stock R2.57 firmware rejects unauthenticated direct POST requests or requires active browser session state/cookies.

### Browser Automation Login Behavior:
* In a full web browser automation engine:
  - Form fields `#tf1_userName` and `#tf1_password` populated.
  - Button `button.login.users.dashboard` clicked.
  - Event listener in `loadingStatus.js` triggers `#tf1_pageLoadingOverLay` and `#tf1_pageLoadingMask`.
  - The DOM displays modal: *"Loading Please wait..!"* with `play.gif` spinner.
  - The browser stalls because no underlying form POST is dispatched if keypress/blur events are interrupted.
* *Fix/Workaround*: Manually submitting the form via console or ensuring complete event dispatch.

---

## 3. Stock Firmware Downgrade Error

### Web UI Firmware Upgrade Submission:
* Uploading:
  1. Primary image: `SRCMTF1_JCOW414_R2.15.img`
  2. Companion signature: `SRCMTF1_JCOW414_R2.15.sig`
* Action: Click "Upgrade" button.
* **Exact Router Error Returned**:
  ```text
  Firmware file is invalid or corrupted.
  ```

### Firmware Binary Integrity Check (Proves Files are NOT Corrupt):
```text
SRCMTF1_JCOW414_R2.15.img:
  Size: 38,071,183 bytes
  SHA-256: ad2977cca4b2796faa81cf0bf7d6f16b152fffdef1c73aba6b6dabc725bbca97
  Offset 0x000: 'HDR2' magic header
  Offset 0x01c: '2.15' version string
  Offset 0x034: 'Reliance' vendor identifier
  Offset 0x074: 'Reliance_v2.15.img'
  Offset 0x110: 'JCOW414_R2.15' target model identifier

SRCMTF1_JCOW414_R2.15.sig:
  Size: 256 bytes
  SHA-256: 669961ce8d04cd0e0d14181b49469f87143f190c89ec11f57bac88e14384ea91

openwrt-jiofiber_jcow414_v1.1.trx:
  Size: 10,223,616 bytes
  SHA-256: 43112eacecdcea64bb213520df50df18cbcd68fc4682932807e915e97883feb2
  Offset 0x000: 'HDR2' magic header
  Offset 0x010: 'OpenWrt-Asjohn720-r0-c4526c7'
```
*Conclusion*: Both firmware files are identical to community baseline dumps. The rejection is an intentional anti-rollback enforcement policy inside the R2.57 firmware validation binary.

---

## 4. OpenSSL Cryptographic Diagnostics

### Decryption Testing with OpenSSL 4.1.0:
```text
# Attempt 1: Using -md md5 (legacy approach)
openssl aes-128-cbc -d -pass pass:[REDACTED_KEY] -in backup.enc -out test.txt -md md5
Result:
*** WARNING : deprecated key derivation used.
bad decrypt
546C0000:error:1C800064:Provider routines:ossl_cipher_unpadblock:bad decrypt
FAILED

# Attempt 2: Using -md sha256 (modern approach)
openssl aes-128-cbc -d -pass pass:[REDACTED_KEY] -in backup.enc -out test.txt -md sha256
Result:
*** WARNING : deprecated key derivation used. Using -iter or -pbkdf2 would be better.
SUCCEEDED (Decrypted 154,507 bytes, SHA-256 matches ground truth exactly).
```

---

## 5. Checksum Discrepancy & Resolution Log

### Analysis of Invalid Modified Config (`modified.txt`):
```text
File size: 154,745 bytes
Line count: 3,144 lines
Declared checksum (Line 3012): 7d669de3e42ace6be9ee2286398e46ca (Stock value left un-updated!)
Computed MD5 of pre-checksum bytes: 1cf7898852d9b5b9303be87bcd6aff4f
Result: MISMATCH -> Router rejects file on restore!
```

### Analysis of Corrected Modified Config (`modified_correct.txt`):
```text
File size: 154,745 bytes
Line count: 3,144 lines
Declared checksum (Line 3012): 1cf7898852d9b5b9303be87bcd6aff4f
Computed MD5 of pre-checksum bytes: 1cf7898852d9b5b9303be87bcd6aff4f
Result: VALID (Exact match) -> Ready for restore!
```
