# BitLocker Auto-Mount Script

## Purpose

This script automatically decrypts and mounts BitLocker-encrypted hard drive partitions on Linux.
It is particularly useful for dual-boot systems where Windows partitions are encrypted with BitLocker but need to be accessed from Linux.
The script supports two methods to unlock BitLocker partitions:
- **User password** – The standard BitLocker password used for unlocking the drive.
- **Recovery key** – A 48-digit recovery key, useful if the password is unavailable.

## Setup

### **1. File Setup**

1. **Download and Extract:**
   - Download the script's ZIP file.
   - Extract it and place the folder in a location of your choice.

2. **Update Path:**
   - In [`bitlocker-startup.sh`](./bitlocker-startup.sh), replace `SCRIPT_FOLDER_LOCATION` with the full path to to the script folder.

### **2. Install dependencies**

#### **Dislocker (Required to Unlock BitLocker Partitions)**  
```bash
sudo apt install dislocker
```

#### **Python Packages (Required for Decryption & Input Handling)**  
```bash
pip install cryptography
pip install getpass_asterisk
```

### **3. Configure [`drives.json`](./drives.json)**

Create or edit `drives.json` to store your BitLocker partition details.

Each drive entry must include:  
- **`NAME`**: A label for the drive (e.g., `"ssd1"`).  
- **`PARTUUID`**: The unique identifier of the partition.  
- **`PASSWORD`**: Either the **BitLocker password** or **48-digit recovery key**.

#### **How to Find the `PARTUUID` of Your Partition:**  
Run the following command:  
```bash
lsblk -o NAME,PARTUUID,FSTYPE,MOUNTPOINT
```

### 4. **Encrypt `drives.json`**

Once `drives.json` is ready, encrypt it for security using [`encrypt.py`](./encrypt.py).

You will be prompted to enter a **password**, which will be required to decrypt the file later.

### 5. Secure `drives.json`

After encrypting `drives.json`, delete the unencrypted version to protect your drive passwords.
If you may need to edit the drive information later, store an unencrypted backup on an **encrypted partition**. Only the encrypted *drives.json.enc* should be kept for regular use.

However, **if your entire Linux system is already encrypted**, keeping the unencrypted *drives.json* is generally safe.

### 6. Add the Script to Startup

To ensure the script runs automatically at startup, add the following command to your **startup applications**:

```bash
/SCRIPT_FOLDER_LOCATION/bitlocker-startup.sh
```
It is necessary to allow executing the .sh file as a program. To do this, run:
```bash
chmod +x /SCRIPT_FOLDER_LOCATION/bitlocker-startup.sh
```

## Usage

After logging in, a terminal will automatically open, prompting you to:

1. Enter your user login password for `sudo` permissions.
2. Enter the password that was used to encrypt `drives.json`.

Once both passwords are entered correctly, the script will decrypt the `drives.json.enc` file and proceed to unlock and mount your BitLocker-encrypted drives.

## **Compatibility**

This script has been **tested on Ubuntu 22.04**.

It should work on other **Debian-based** distributions (such as Debian, Linux Mint, and Pop!_OS), but additional testing may be required. 

If you encounter issues:
- Try installing the [dislocker](https://github.com/Aorimn/dislocker) and [ntfs-3g](https://github.com/tuxera/ntfs-3g) packages manually.
