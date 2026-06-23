# 🚀 iCloud Family Automation Suite

Advanced Apple Family Sharing Automation Framework built with Python, UIAutomator2, ADB, Multi-Threading and CustomTkinter.

Designed for large-scale account management, child account creation, Family Sharing automation, birthday aging, and Android emulator orchestration.

---

# ✨ Features

## Account Management

- Apple ID Login Automation
- Security Questions Handling
- Session Recovery
- Session Regeneration
- Multi-Account Processing

## Family Sharing

- Create Child Accounts
- Remove Child Accounts
- Reset Family Sharing
- Organizer Verification
- Family Sharing Recovery

## Aging System

- Apple SRP Authentication
- Birthday Verification
- Birthday Update
- Retry Logic
- Proxy Support

## Android Automation

- UIAutomator2 Integration
- ADB Support
- Fast Element Detection
- Smart Waiting System
- Activity Management

## GUI Dashboard

- Modern Dark Theme
- CSV Import
- Live Logs
- Progress Tracking
- Start / Stop Controls
- Multi-Thread Support

---

# 🏗 Architecture

```text
Main Controller
│
├── Emulator Manager
│
├── Family Sharing Module
│
├── Child Creation Module
│
├── Aging Module
│
├── Retry Engine
│
├── Logging System
│
└── GUI Dashboard
```

---

# 📱 Emulator Management

Supported:

- LDPlayer
- Android Emulator
- Any ADB-Compatible Emulator

Capabilities:

- Multi-Instance Support
- Auto Reconnect
- Auto Recovery
- Parallel Execution
- Worker Isolation

---

# 🤖 Android Automation

Powered By:

- UIAutomator2
- ADB
- Python

Features:

- Smart Click Detection
- Fast UI Navigation
- Dynamic Wait System
- Activity Launching
- Error Recovery

---

# 👤 Apple Authentication

The project uses Apple's authentication flow including:

- Apple ID Authentication
- Session Management
- Security Questions Verification
- Session Recovery
- Re-Authentication

---

# 👨‍👩‍👧 Family Sharing Automation

Supported Operations:

- Open Family Sharing
- Create Child
- Remove Child
- Verify Organizer
- Family Reset
- Family Cleanup

Error Handling:

- Cannot Start Family Sharing
- Maximum Invitations Reached
- Session Expired
- Family Sharing Unavailable
- Temporary Apple Errors

---

# 🎂 Aging Module

Automatically updates child account birthdays.

Features:

- SRP Authentication
- Birthday Verification
- Birthday Update
- Automatic Retry
- Session Recovery

Default Example:

```text
01/01/1990
```

Output:

```text
aging_success.csv
```

Failed Accounts:

```text
accounts.csv
```

---

# 🌐 Proxy Support

Supported Formats

## HTTP

```text
ip:port
```

## HTTP Auth

```text
ip:port:user:password
```

## SOCKS4

```text
socks4://ip:port
```

## SOCKS5

```text
socks5://ip:port
```

## SOCKS5 Auth

```text
socks5://user:pass@ip:port
```

---

# ⚡ Multi Threading

Implemented Using:

```python
ThreadPoolExecutor
threading
```

Features:

- Parallel Aging
- Parallel Processing
- Background Workers
- Thread-Safe GUI Updates

---

# 🖥 GUI Features

Built With:

```text
CustomTkinter
```

Features:

- Modern Dark Theme
- Responsive Layout
- Colored Logs
- CSV File Selection
- Progress Bar
- Live Status Updates

Log Types:

| Status | Color |
|----------|----------|
| Processing | 🔵 Blue |
| Success | 🟢 Green |
| Retry | 🟡 Yellow |
| Error | 🔴 Red |
| Info | ⚪ White |

---

# 📂 Project Structure

```text
project/
│
├── main.py
├── aging.py
├── family.py
├── utils.py
├── config.ini
│
├── accounts.csv
├── accounts.txt
├── done.txt
├── fail.txt
├── locked.txt
├── aging_success.csv
│
├── logs/
│
└── gui/
```

---

# ⚙ Configuration

config.ini

```ini
[Settings]

use_proxy = false
proxy =

[Child]

password = Example123
answer1 = answer1
answer2 = answer2
answer3 = answer3
```

---

# 📄 CSV Format

```csv
email,password,ans1,ans2,ans3
example@icloud.com,password,ans1,ans2,ans3
```

---

# 📁 Output Files

## accounts.txt

Successfully created child accounts.

## done.txt

Processed accounts.

## fail.txt

Failed accounts.

## locked.txt

Locked Apple IDs.

## aging_success.csv

Successfully aged accounts.

---

# 🔄 Retry System

Automatically Handles:

- Login Failures
- Session Expiration
- Aging Failures
- Family Sharing Failures
- Temporary Apple Errors

Detected Errors:

```text
401 Unauthorized
boot_args missing
cannot be completed
session burned
```

---

# 🛡 Recovery System

Automatic Recovery For:

- Session Expiration
- Login Failure
- Family Sharing Failure
- Child Creation Failure
- Aging Failure

---

# 📊 Logging System

Examples:

```text
[→] Processing
[✓] Success
[✗] Failed
[!] Warning
```

---

# 📈 Performance

Recommended Usage

```text
1 Emulator  = Light Usage
3 Emulators = Medium Usage
5+ Emulators = Heavy Usage
```

Supports:

- Long Running Sessions
- Large Account Batches
- Multi Emulator Environments

---

# 📦 Requirements

Python:

```text
Python 3.10+
```

Dependencies:

```bash
pip install requests
pip install colorama
pip install termcolor
pip install cryptography
pip install libsrp
pip install uiautomator2
pip install customtkinter
pip install psutil
pip install faker
pip install wmi
```

---

# 🚀 Installation

Clone Repository

```bash
git clone <repository>
cd project
```

Install Requirements

```bash
pip install -r requirements.txt
```

Configure

```text
config.ini
```

Run

```bash
python main.py
```

---

# 🔧 Troubleshooting

## Emulator Not Found

```bash
adb devices
```

Check ADB connection.

---

## Family Sharing Errors

Verify:

- Organizer Status
- Internet Connection
- Apple Account Status

---

## Aging Failures

Verify:

- Security Answers
- Proxy Settings
- Apple Session
- Birthday Format

---

# 👨‍💻 Authors

Discord:

```text
mazenmahmoud6550
som3aa2001
```

---

# 📜 License

Private Project

All Rights Reserved

---

# ⚠ Disclaimer

This software is provided for educational and research purposes only.

Users are responsible for ensuring compliance with applicable laws, regulations, and platform terms of service.

Use at your own risk.
