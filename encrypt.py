from getpass_asterisk.getpass_asterisk import getpass_asterisk
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
import base64
import os


def generate_key_from_password(password: str, salt: bytes) -> bytes:
    """Generate a key from a password and salt using PBKDF2HMAC."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend(),
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key


def encrypt_file(password: str, file_path: str, output_path: str):
    """Encrypt the content of a file with a password."""
    salt = os.urandom(16)  # Create a random salt
    key = generate_key_from_password(password, salt)
    fernet = Fernet(key)

    # Read the content of the file to encrypt
    with open(file_path, "rb") as file:
        file_data = file.read()

    # Encrypt the file data
    encrypted_data = fernet.encrypt(file_data)

    # Write the salt and encrypted data to the output file
    with open(output_path, "wb") as file:
        file.write(salt + encrypted_data)


# Example: Encrypt the "drives.json" file
password = getpass_asterisk("Enter a password to encrypt the file: ")
encrypt_file(password, "drives.json", "drives.json.enc")
print("File encrypted and saved as 'drives.json.enc'")
