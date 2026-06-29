import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from config import Config
import os


def get_encryption_key():
    """Generate or retrieve Fernet key from SECRET_KEY"""
    secret_key = Config.SECRET_KEY.encode()
    salt = b'linkedin-automation-salt'  # Fixed salt for consistency
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(secret_key))
    return key


def encrypt_api_key(api_key: str) -> str:
    """Encrypt API key before storing"""
    key = get_encryption_key()
    fernet = Fernet(key)
    encrypted = fernet.encrypt(api_key.encode())
    return base64.urlsafe_b64encode(encrypted).decode()


def decrypt_api_key(encrypted_api_key: str) -> str:
    """Decrypt API key after retrieving from DB"""
    key = get_encryption_key()
    fernet = Fernet(key)
    encrypted = base64.urlsafe_b64decode(encrypted_api_key.encode())
    return fernet.decrypt(encrypted).decode()
