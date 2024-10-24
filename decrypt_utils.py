from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
import base64


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


def decrypt_file(password: str, file_path: str) -> bytes:
    """Decrypt the encrypted file with the provided password."""
    try:
        # Read the salt (first 16 bytes) and the encrypted data
        with open(file_path, "rb") as file:
            salt = file.read(16)  # First 16 bytes are the salt
            encrypted_data = file.read()  # The rest is the encrypted data

        # Generate the key from the password and salt
        key = generate_key_from_password(password, salt)
        fernet = Fernet(key)

        # Decrypt the data
        decrypted_data = fernet.decrypt(encrypted_data)
        return decrypted_data
    except Exception as e:
        raise ValueError(f"Failed to decrypt the file: {e}")
