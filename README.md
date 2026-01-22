# A ClassChat System
## README Documentation

**Md Farukuzzaman Faruk**  
Program: PhD in CS  
School of Computing and Informatics  
University of Louisiana at Lafayette  


---

## Table of Contents

1. [Project Overview](#1-project-overview)
   - 1.1 [Description](#11-description)
   - 1.2 [Purpose](#12-purpose)
2. [Key Features](#2-key-features)
3. [System Requirements](#3-system-requirements)
   - 3.1 [Software Requirements](#31-software-requirements)
   - 3.2 [Python Package Dependencies](#32-python-package-dependencies)
   - 3.3 [Hardware Requirements](#33-hardware-requirements)
4. [Installation](#4-installation)
   - 4.1 [Download Project](#41-download-project)
   - 4.2 [Install Dependencies](#42-install-dependencies)
   - 4.3 [Verify Installation](#43-verify-installation)
5. [Usage Instructions](#5-usage-instructions)
   - 5.1 [Quick Start (Using Launcher)](#51-quick-start-using-launcher---recommended)
   - 5.2 [Manual Execution](#52-manual-execution)
   - 5.3 [Using Makefile](#53-using-makefile-linuxmacgit-bash)
6. [Project Structure](#6-project-structure)
   - 6.1 [File Organization](#61-file-organization)
   - 6.2 [Module Descriptions](#62-module-descriptions)
   - 6.3 [Database Schema](#63-database-schema)
7. [Configuration](#7-configuration)
8. [Common Usage Scenarios](#8-common-usage-scenarios)
9. [Troubleshooting](#9-troubleshooting)
10. [Testing](#10-testing)
11. [Documentation](#11-documentation)

---

## 1. Project Overview

### 1.1 Description

ClassChat is a full-featured client-server chat application. The system demonstrates advanced network programming concepts including TCP/IP socket programming, multi-threading, I/O multiplexing, and cryptographic protocols.

### 1.2 Purpose

This project was developed to gain hands-on experience with:

- Low-level network programming using TCP/IP sockets
- Concurrent server design with thread synchronization
- Efficient I/O handling through multiplexing techniques
- Secure communication using hybrid encryption (RSA + AES)
- Database-backed persistent storage
- GUI application development

---

## 2. Key Features

ClassChat implements the following functionality:

### 1. TCP/IP Socket Communication
- Client-server architecture using Python sockets
- Server listening on `127.0.0.1:5555`
- Reliable TCP connection with automatic reconnection support

### 2. Multi-Threaded Server
- Concurrent handling of multiple clients (tested up to 50+)
- Thread-per-client architecture with daemon threads
- Thread synchronization using `threading.Lock()`
- Race condition prevention for shared resources

### 3. I/O Multiplexing
- Platform-adaptive: `epoll()` (Linux), `poll()` (Unix), `select()` (Windows)
- Non-blocking socket operations
- Efficient handling of multiple simultaneous connections

### 4. Hybrid Encryption (RSA-2048 + AES-256-CBC)
- RSA-2048 for secure session key exchange
- AES-256-CBC for message encryption
- Unique session keys per client connection
- PKCS7 padding with random IVs

### 5. Private Messaging
- Direct client-to-client communication via server routing
- Real-time message delivery
- Message persistence in SQLite database

### 6. Group Chat
- Create and join multiple chat groups
- Broadcast messaging to all group members
- Group membership management

### 7. File Transfer
- Send files up to 10MB
- Support for individual and group file sharing
- Base64 encoding with encryption
- No server-side file storage (routing only)

### 8. Offline Message Handling
- Automatic message queuing for offline users
- Delivery upon reconnection
- Persistent storage in SQLite database

### 9. Graphical User Interface
- Tkinter-based client GUI
- Unified launcher for server and client management
- Real-time system resource monitoring (CPU/Memory)
- Responsive interface with background threading

### 10. JSON Protocol
- Structured message format
- Human-readable for debugging
- Extensible message types
- Language-agnostic design

---

## 3. System Requirements

### 3.1 Software Requirements

| Component | Requirement |
|-----------|-------------|
| Python | 3.8 or higher (tested on 3.12) |
| Operating System | Windows 10/11, Linux (Ubuntu 20.04+), macOS 10.15+ |
| Database | SQLite3 (included with Python) |
| IDE (Optional) | PyCharm (Used in this project), VS Code, or any Python IDE |

### 3.2 Python Package Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| cryptography | ≥ 41.0.0 | RSA-2048 and AES-256-CBC encryption |
| Pillow | ≥ 9.0.0 | GUI image handling |
| psutil | ≥ 5.9.0 | System resource monitoring |
| pycryptodome | Latest | Additional cryptographic functions |

**Note:** Standard library modules (`socket`, `threading`, `json`, `tkinter`, `sqlite3`, `select`) are included with Python.

### 3.3 Hardware Requirements

- **Minimum:** 4 GB RAM, dual-core processor, 500 MB disk space
- **Recommended:** 8 GB RAM, quad-core processor, 1 GB disk space
- **Network:** Loopback interface (127.0.0.1) for local testing

---

## 4. Installation

### 4.1 Download Project

Download and extract the project:

```bash
# Extract from ZIP
unzip ClassChat-Project.zip

# Navigate to main project directory
cd ClassChat-Project

# Navigate to source code directory
cd "ClassChat-All-Python-and-Necessary-Files"
```


**Note:** All Python source files are located in the `ClassChat-All-Python-and-Necessary-Files/` subdirectory.

### 4.2 Install Dependencies

#### 4.2.1 Method 1: Using pip (Recommended)

```bash
# Install required packages
pip install cryptography>=41.0.0
pip install Pillow>=9.0.0
pip install psutil>=5.9.0
pip install pycryptodome
```

#### 4.2.2 Method 2: Using requirements.txt

```bash
pip install -r requirements.txt
```

#### 4.2.3 Method 3: Using Virtual Environment (Best Practice)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 4.3 Verify Installation

```bash
python -c "import cryptography, PIL, psutil; print('All dependencies installed successfully!')"
```

---

## 5. Usage Instructions

### 5.1 Quick Start (Using Launcher) - Recommended

The easiest way to run ClassChat is using the unified launcher:

1. Launch the GUI control panel:
   ```bash
   python launcher.py
   ```
   Or by clicking "Run launcher" in PyCharm.

2. Click **START SERVER** button to start the server
3. Click **START CLIENT** button to launch a client (repeat for multiple clients)
4. Enter username when prompted and connect to the server
5. Start chatting!

### 5.2 Manual Execution

For more control, run server and clients separately:

#### 5.2.1 Step 1: Start the Server

Open a terminal and run:

```bash
python server.py
```

**Expected output:**
```
[DATABASE] Database initialized with message history support
[SERVER] Generating RSA key pair...
[SERVER] RSA keys generated successfully
[SERVER] 🔒 Encryption ENABLED
[SERVER] ClassChat Server started on 127.0.0.1:5555
[SERVER] Waiting for connections...
```

#### 5.2.2 Step 2: Start Client(s)

Open one or more additional terminals and run:

```bash
python client.py
```

#### 5.2.3 Step 3: Connect and Chat

1. Enter a username (e.g., Alice, Bob, Zara)
2. Click **Connect** button
3. Select a recipient from the user list
4. Type a message and click **Send**

### 5.3 Using Makefile (Linux/Mac/Git Bash)

If you have `make` installed:

```bash
make help       # Display all available commands
make setup      # Setup virtual environment and install dependencies
make run        # Launch the GUI launcher
make server     # Run server only
make client     # Run client only
make demo       # Run server + 2 clients
make clean      # Remove cache files
make db-reset   # Reset database to initial state
```

---

## 6. Project Structure

### 6.1 File Organization

```
ClassChat-Project/                             Main project directory
└── ClassChat-All-Python-and-Necessary-Files/  Source code folder
    ├── launcher.py                            GUI control panel
    ├── server.py                              Multi-threaded server
    ├── client.py                              GUI client
    ├── encryption.py                          RSA + AES encryption
    ├── config.py                              Configuration
    ├── protocol.py                            Message protocols
    ├── database.py                            SQLite operations
    ├── io_multiplexer.py                      I/O multiplexing
    ├── requirements.txt                       Dependencieso
    ├── Makefile                               Build automation
    ├── classchat.db                           Database (auto-created)
    └── Files-to-used-for-demo-purpose/        Demo file sending
├── ClassChat_README_File.md                   Documentation (Markdown)
├── ClassChat_Demo_Video.mp4                   Demo video
└── Makefile                                   Build automation
```

### 6.2 Module Descriptions

| File | Description |
|------|-------------|
| `launcher.py` | Tkinter-based GUI for starting/stopping server and clients using `subprocess.Popen()` |
| `server.py` | Multi-threaded server implementing thread-per-client architecture with synchronization |
| `client.py` | GUI client with background receive thread and system monitoring |
| `encryption.py` | Hybrid encryption: RSA key generation/exchange + AES message encryption |
| `protocol.py` | JSON message protocol with `create_message()` and `parse_message()` methods |
| `database.py` | SQLite wrapper for users, messages, groups, and offline_messages tables |
| `io_multiplexer.py` | Platform-adaptive I/O multiplexing (select/poll/epoll) |
| `config.py` | Configuration constants (HOST, PORT, BUFFER_SIZE, etc.) |

### 6.3 Database Schema

The SQLite database (`classchat.db`) contains four tables:

1. **users:** `(username, created_at)`
2. **messages:** `(id, sender, receiver, message_type, content, timestamp)`
3. **groups:** `(id, group_name, creator, created_at)`
4. **offline_messages:** `(id, receiver, sender, message_type, content, delivered, timestamp)`

---

## 7. Configuration

Edit `config.py` to customize server settings:

```python
# Network Settings
HOST = '127.0.0.1'      # Server IP address (localhost)
PORT = 5555             # Server port
BUFFER_SIZE = 131072    # 128 KB socket buffer

# File Transfer
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB maximum file size

# Security
USE_ENCRYPTION = True   # Enable/disable encryption

# Database
DB_NAME = 'classchat.db'  # SQLite database filename
```

---

## 8. Common Usage Scenarios

### 8.1 Scenario 1: Private Messaging

1. Start server and connect two clients (Alice and Bob)
2. In Alice's client: Select Bob from user list
3. Type message: "Hello Bob!"
4. Click **Send**
5. Bob receives message instantly
6. Both clients see message in chat history

### 8.2 Scenario 2: Creating and Joining Groups

1. Alice creates group:
   - Click **+Create** button
   - Enter group name: "CSCE-513"
   - Click **Create** again

2. Bob joins group:
   - See "CSCE-513" in group list
   - Double-click or select and click **JOIN**
   - Confirmation: "Joined CSCE-513"

3. Send group message:
   - Select "CSCE-513" from group list
   - Type message
   - All group members receive message

### 8.3 Scenario 3: File Transfer

1. Select recipient (individual or group)
2. Click **Attach** button and select a file from a directory
3. Click **File Send** button
4. Choose file from file dialog (max 10MB)
5. File is encoded (base64), encrypted, and sent
6. Recipient(s) receive file transfer notification
7. Click notification to save file to desired location

### 8.4 Scenario 4: Offline Message Delivery

1. Bob is offline (client closed)
2. Alice sends message to Bob
3. Server queues message in `offline_messages` table
4. Bob reconnects later
5. Upon connection, server delivers all queued messages
6. Messages appear in Bob's chat history

---

## 9. Troubleshooting

### 9.1 Common Issues and Solutions

#### 9.1.1 Issue 1: "Address already in use" Error

**Symptom:** Server fails to start with error `[Errno 98] Address already in use`

**Cause:** Port 5555 is occupied by another process

**Solution:**

Windows:
```bash
# Find process using port 5555
netstat -ano | findstr :5555

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

Linux/Mac:
```bash
# Find and kill process
lsof -ti:5555 | xargs kill -9

# Or change port in config.py
```

#### 9.1.2 Issue 2: "Module not found" Errors

**Symptom:** `ModuleNotFoundError: No module named 'cryptography'`

**Cause:** Required packages not installed

**Solution:**
```bash
# Reinstall all dependencies
pip install -r requirements.txt --upgrade

# Verify installation
python -c "import cryptography, PIL, psutil"
```

#### 9.1.3 Issue 3: Client Cannot Connect to Server

**Symptom:** Client shows "Connection refused" or timeout

**Cause:** Server not running or firewall blocking connection

**Solution:**
1. Verify server is running: Check terminal for "Listening on 127.0.0.1:5555"
2. Check firewall settings: Allow Python on port 5555
3. Verify host/port in client matches server configuration
4. Try disabling firewall temporarily for testing

#### 9.1.4 Issue 4: GUI Freezing or Not Responsive

**Symptom:** Client GUI becomes unresponsive during operations

**Cause:** Network operations blocking main thread

**Solution:**
1. Ensure `receive_messages()` thread is running as daemon
2. Check console for error messages
3. Restart client
4. If persistent, check CPU/memory usage (may indicate resource exhaustion)

#### 9.1.5 Issue 5: Encryption Errors

**Symptom:** Messages not decrypting correctly or encryption failures

**Cause:** Key exchange failure or corrupted session keys

**Solution:**
1. Disconnect and reconnect client (triggers new key exchange)
2. Delete `classchat.db` and restart server (resets all keys)
3. Check that `USE_ENCRYPTION = True` in `config.py`
4. Verify cryptography package version ≥ 41.0.0

---

## 10. Testing

### 10.1 Basic Functionality Tests

#### 10.1.1 Test 1: Server Startup

1. Run `python server.py`
2. Verify output: "Listening on 127.0.0.1:5555"
3. Expected: Server starts without errors

#### 10.1.2 Test 2: Single Client Connection

1. Start server
2. Run `python client.py`
3. Enter username and connect
4. Expected: Connection successful, user appears in server log

#### 10.1.3 Test 3: Private Messaging

1. Connect two clients (Alice, Bob)
2. Alice sends message to Bob
3. Expected: Bob receives message immediately
4. Verify message appears in both chat histories

#### 10.1.4 Test 4: Multi-Client Concurrency

1. Start server
2. Connect 4+ clients simultaneously
3. Have all clients send messages concurrently
4. Expected: All messages delivered correctly, no blocking

#### 10.1.5 Test 5: Offline Message Delivery

1. Connect Alice, keep Bob offline
2. Alice sends message to Bob
3. Bob connects
4. Expected: Bob receives queued message upon connection

#### 10.1.6 Test 6: File Transfer

1. Connect two clients
2. Send a small file
3. Expected: File transferred successfully and can be saved

#### 10.1.7 Test 7: Encryption Verification

1. Enable `USE_ENCRYPTION = True`
2. Send message between clients
3. Check server logs for encrypted data (base64 strings)
4. Expected: Raw encrypted data visible, decrypted correctly

---

## 11. Documentation

### 11.1 Available Documentation

1. **This README:** Quick start and usage guide

3. **Makefile:** Run `make help` for command reference

---

**End of README**
