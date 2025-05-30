import json
import os
import re
import subprocess
from typing import Optional, Tuple

from getpass_asterisk.getpass_asterisk import getpass_asterisk

from decrypt_utils import decrypt_file

USERNAME = os.getenv("USER") or os.getlogin()
USER_UID = os.getuid()
USER_GID = os.getgid()


def load_encrypted_json(encrypted_file_path):
    """Load and decrypt the encrypted JSON file."""

    # Check if the file exists
    if not os.path.exists(encrypted_file_path):
        print(f"Error: Encrypted file '{encrypted_file_path}' not found.")
        return None

    while True:
        password = getpass_asterisk("Enter the password to decrypt 'drives.json.enc': ")
        try:
            # Attempt to decrypt the file
            decrypted_json_data = decrypt_file(password, encrypted_file_path)
            # Parse and return the JSON content if decryption succeeds
            return json.loads(decrypted_json_data.decode("utf-8"))
        except ValueError:
            print("Incorrect password. Please try again.")
        except json.JSONDecodeError:
            print("Error: Decrypted data is not valid JSON.")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None


def sudo_makedirs(path):
    """Create a directory with sudo."""
    subprocess.run(["sudo", "mkdir", "--parents", path], check=True)


def prepare_mount_points(
    drive, uid=USER_UID, gid=USER_GID
) -> Tuple[Optional[str], Optional[str]]:
    """Prepare the directories for mounting the drives.

    Args:
        drive (str): The name of the drive (e.g., "sda1").

    Returns:
        Tuple[Optional[str], Optional[str]]: Paths to the BitLocker mount point
        and the drive mount point, or (None, None) if an error occurs.
    """
    try:
        # Create a separate directory for each drive under /mnt/dislocker/
        bitlocker_mount_point = f"/mnt/dislocker/{drive}"
        if not os.path.exists(bitlocker_mount_point) or not os.listdir(
            bitlocker_mount_point
        ):
            sudo_makedirs(bitlocker_mount_point)
            print(f"Created BitLocker mount directory: {bitlocker_mount_point}")

        # Create the drive-specific mount point if it doesn't exist or is empty
        drive_mount_point = f"/media/{USERNAME}/{drive}"
        if not os.path.exists(drive_mount_point) or not os.listdir(drive_mount_point):
            sudo_makedirs(drive_mount_point)
            print(f"Created mount directory: {drive_mount_point}")

        return bitlocker_mount_point, drive_mount_point

    except OSError as e:
        print(f"Error creating mount directories: {e}")
        return None, None


def unlock_drive(drive, partuuid, password, bitlocker_mount_point) -> bool:
    """Unlock the BitLocker encrypted drive."""
    # Regex pattern for BitLocker recovery key
    recovery_key_pattern = re.compile(
        r"^\d{6}-\d{6}-\d{6}-\d{6}-\d{6}-\d{6}-\d{6}-\d{6}$"
    )

    # Determine the correct option
    if recovery_key_pattern.match(password):
        password_option = f"--recovery-password={password}"
    else:
        password_option = f"--user-password={password}"

    dislocker_cmd = [
        "sudo",
        "dislocker",
        "--verbosity",
        "--volume",
        f"/dev/disk/by-partuuid/{partuuid}",
        password_option,
        "--",
        bitlocker_mount_point,
    ]
    print(f"Unlocking drive {drive}...")
    try:
        result = subprocess.run(
            dislocker_cmd, check=True, capture_output=True, text=True
        )
        print("Drive unlocked successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error unlocking drive {drive}:")
        print(f"Return code: {e.returncode}")
        print(f"Standard output:\n{e.stdout}")
        print(f"Error output:\n{e.stderr}")
        return False


def mount_drive(bitlocker_mount_point, drive_mount_point) -> bool:
    """
    Mount the unlocked drive.
    Set the mount options to allow read/write access for the current user.
    """
    mount_cmd = [
        "sudo",
        "mount",
        "--options",
        f"loop,rw,uid={USER_UID},gid={USER_GID},umask=0077,dmask=0077,fmask=0077",
        f"{bitlocker_mount_point}/dislocker-file",
        drive_mount_point,
    ]
    print(f"Mounting drive to {drive_mount_point}...")
    try:
        result = subprocess.run(mount_cmd, check=True, capture_output=True, text=True)
        print("Drive mounted successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error mounting drive to {drive_mount_point}:")
        print(f"Return code: {e.returncode}")
        print(f"Standard output:\n{e.stdout}")
        print(f"Error output:\n{e.stderr}")
        return False


def ensure_sudo():
    """Ensure the script is run with sudo privileges."""
    try:
        subprocess.run(["sudo", "true"], check=True)
    except subprocess.CalledProcessError:
        print("Error: Failed to obtain sudo privileges. Exiting.")
        raise SystemExit


def main():
    print("===== BitLocker Unlock and Mount Script =====")
    print("Script starting...")

    # Ensure sudo privileges before proceeding
    ensure_sudo()

    # Get the path to the current directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Full path to the 'drives.json.enc' file
    json_file_path = os.path.join(script_dir, "drives.json.enc")

    # Load the decrypted JSON data
    data = load_encrypted_json(json_file_path)
    if not data:
        print(
            "Error: Could not load or decrypt 'drives.json.enc'. Make sure the file exists and the correct password is entered."
        )
        return
    print("")

    total_drives = len(data["drives"])
    unlocked_count = 0
    mounted_count = 0
    failed_unlock = []
    failed_mount = []

    # Iterate over each entry in the JSON and handle unlocking/mounting
    for entry in data["drives"]:
        drive_name = entry["NAME"]
        drive_partuuid = entry["PARTUUID"]
        drive_password = entry["PASSWORD"]

        if not all([drive_name, drive_partuuid, drive_password]):
            print(f"Skipping entry due to missing information: {entry}")
            continue

        # Prepare the mount points
        bitlocker_mount_point, drive_mount_point = prepare_mount_points(drive_name)
        if bitlocker_mount_point is None or drive_mount_point is None:
            print(f"Error: Failed to prepare mount points for {drive_name}.")
            continue

        # Unlock the BitLocker encrypted drive
        if not unlock_drive(
            drive_name, drive_partuuid, drive_password, bitlocker_mount_point
        ):
            print(f"Error: Failed to unlock {drive_name}.")
            failed_unlock.append(drive_name)
            continue
        unlocked_count += 1

        # Mount the unlocked drive
        if not mount_drive(bitlocker_mount_point, drive_mount_point):
            print(f"Error: Failed to mount {drive_name}.")
            failed_mount.append(drive_name)
            continue
        mounted_count += 1

        print(f"{drive_name} is successfully unlocked and mounted.\n")

    # **Final Summary**
    print("===== Summary =====")
    print(f"Total drives processed: {total_drives}")
    print(f"Successfully unlocked: {unlocked_count}/{total_drives}")
    print(f"Successfully mounted: {mounted_count}/{total_drives}")

    if failed_unlock:
        print(f"Failed to unlock: {', '.join(failed_unlock)}")

    if failed_mount:
        print(f"Failed to mount (after unlocking): {', '.join(failed_mount)}")

    if unlocked_count == total_drives and mounted_count == total_drives:
        print("All drives were successfully unlocked and mounted!")
    else:
        print("Some drives encountered issues. Please check the errors above.")


if __name__ == "__main__":
    main()
