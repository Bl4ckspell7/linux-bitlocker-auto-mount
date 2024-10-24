# BitLocker Auto-Mount Script

## Purpose

This script automatically decrypts and mounts BitLocker-encrypted hard drive partitions on Linux.
It is especially useful for dual-boot systems where Windows partitions are BitLocker-encrypted and need to be accessed from Linux.

## Setup

### 1. File Setup

1. **Download and Extract:** Download the script's ZIP file, extract it, and place the folder in a location of your choice.

2. **Update Paths and User Information:**
   In [`bitlocker-startup.sh`](./bitlocker-startup.sh), replace `SCRIPT_FOLDER_LOCATION` with the full path to the folder where you placed the script.
   In [`bitlocker-unlock-mount.py`](./bitlocker-unlock-mount.py), replace `YOUR_USERNAME` with your actual Linux username.

### 2. Install dependencies

- **dislocker:** Used to unlock BitLocker-encrypted partitions.

```bash
sudo apt install dislocker
```

- **Python packages:** Install the necessary Python packages using pip:

```bash
pip install cryptography
pip install getpass_asterisk
```

### 3. Fill [`drives.json`](./drives.json) with your data:

For each drive, add a name, PARTUUID and the BitLocker password.

**How to Find the PARTUUID:**

1. Identify your drives (/dev/sdX)

```bash
sudo fdisk -l
```

2. Get the PARTUUID for each drive using:

```bash
sudo blkid | grep BitLocker
```

### 4. Encrypt `drives.json`

Once the `drives.json` is ready, run [`encrypt.py`](./encrypt.py) to encrypt it.

You will be prompted to enter a password, which will be required to decrypt the file later.

### 5. Add the Script to Startup

To ensure the script runs automatically at startup, add the following command to your startup applications:

```bash
/SCRIPT_FOLDER_LOCATION/bitlocker-startup.sh
```

### 6. Secure `drives.json`

After encrypting drives.json, delete the unencrypted version to protect your drive passwords.

If you may need to edit or update the drive information later (e.g., adding more drives or changing BitLocker passwords), store the unencrypted file on an encrypted partition. Only the encrypted `drives.json.enc` should remain accessible for regular use.

## Usage

After logging in, a terminal will automatically open, prompting you to:

1. Enter your user login password for `sudo` permissions.
2. Enter the password that was used to encrypt `drives.json`.

Once both passwords are entered correctly, the script will decrypt the `drives.json.enc` file and proceed to unlock and mount your BitLocker-encrypted drives.
