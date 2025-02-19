import json
import os
import subprocess

from getpass_asterisk.getpass_asterisk import getpass_asterisk

from decrypt_utils import decrypt_file

# Replace with your actual username
USERNAME = "YOUR_USERNAME"


def load_encrypted_json(encrypted_file_path):
    """Load and decrypt the encrypted JSON file."""
    while True:
        password = getpass_asterisk("Enter the password to decrypt 'drives.json.enc': ")
        try:
            # Attempt to decrypt the file
            decrypted_json_data = decrypt_file(password, encrypted_file_path)
            # Parse and return the JSON content if decryption succeeds
            return json.loads(decrypted_json_data.decode("utf-8"))
        except ValueError:
            print("Incorrect password. Please try again.")


def prepare_mount_points(drive):
    """Prepare the directories for mounting the drives."""
    # Create a separate directory for each drive under /mnt/dislocker/
    bitlocker_mount_point = f"/mnt/dislocker/{drive}"
    if not os.path.exists(bitlocker_mount_point):
        os.makedirs(bitlocker_mount_point)
        print(f"Created BitLocker mount directory: {bitlocker_mount_point}")

    # Create the drive-specific mount point if it doesn't exist
    drive_mount_point = f"/media/{USERNAME}/{drive}"
    if not os.path.exists(drive_mount_point):
        os.makedirs(drive_mount_point)
        print(f"Created mount directory: {drive_mount_point}")

    return bitlocker_mount_point, drive_mount_point


def unlock_drive(drive, partuuid, password, bitlocker_mount_point):
    """Unlock the BitLocker encrypted drive."""
    dislocker_cmd = [
        "sudo",
        "dislocker",
        "-v",
        "-V",
        f"/dev/disk/by-partuuid/{partuuid}",
        f"--user-password={password}",
        "--",
        bitlocker_mount_point,
    ]
    print(f"Unlocking drive {drive}...")
    subprocess.run(dislocker_cmd)


def mount_drive(bitlocker_mount_point, drive_mount_point):
    """Mount the unlocked drive."""
    mount_cmd = [
        "sudo",
        "mount",
        "-o",
        "loop,rw",
        f"{bitlocker_mount_point}/dislocker-file",
        drive_mount_point,
    ]
    print(f"Mounting drive to {drive_mount_point}...")
    subprocess.run(mount_cmd)


def main():
    # Get the path to the current directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Full path to the 'drives.json.enc' file
    json_file_path = os.path.join(script_dir, "drives.json.enc")

    # Load the decrypted JSON data
    data = load_encrypted_json(json_file_path)

    # Iterate over each entry in the JSON and handle unlocking/mounting
    for entry in data["drives"]:
        drive_name = entry["NAME"]
        drive_partuuid = entry["PARTUUID"]
        drive_password = entry["PASSWORD"]

        # Prepare the mount points
        bitlocker_mount_point, drive_mount_point = prepare_mount_points(drive_name)

        # Unlock the BitLocker encrypted drive
        unlock_drive(drive_name, drive_partuuid, drive_password, bitlocker_mount_point)

        # Mount the unlocked drive
        mount_drive(bitlocker_mount_point, drive_mount_point)

        print(f"{drive_name} is unlocked and mounted.")


if __name__ == "__main__":
    main()
