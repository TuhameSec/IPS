"""Module for secure encryption and decryption using AES-256-GCM."""
import os
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from logging_config import configure_logging

logger = configure_logging()

def initialize_cipher() -> bytes:
    """Initialize AES-256 key from environment variables."""
    password = os.getenv("ENCRYPTION_PASSWORD")
    if not password:
        logger.error("Encryption password not set")
        raise ValueError("Encryption password required")
    
    salt = base64.b64decode(os.getenv("ENCRYPTION_SALT", base64.b64encode(os.urandom(16)).decode()))
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=1000000)
    return kdf.derive(password.encode())

encryption_key = initialize_cipher()

def encrypt_data(data: str) -> str:
    """Encrypt data using AES-256-GCM.

    Args:
        data: String to encrypt.

    Returns:
        Base64-encoded encrypted data (IV + tag + ciphertext).
    """
    try:
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(encryption_key), modes.GCM(iv))
        encryptor = cipher.encryptor()
        encrypted = encryptor.update(data.encode()) + encryptor.finalize()
        return base64.b64encode(iv + encryptor.tag + encrypted).decode()
    except Exception as e:
        logger.error(f"Encryption failed: {e}")
        raise

def decrypt_data(data: str) -> str:
    """Decrypt data using AES-256-GCM.

    Args:
        data: Base64-encoded encrypted data.

    Returns:
        Decrypted string.
    """
    try:
        raw = base64.b64decode(data)
        iv, tag, encrypted = raw[:16], raw[16:32], raw[32:]
        cipher = Cipher(algorithms.AES(encryption_key), modes.GCM(iv, tag))
        decryptor = cipher.decryptor()
        return (decryptor.update(encrypted) + decryptor.finalize()).decode()
    except Exception as e:
        logger.error(f"Decryption failed: {e}")
        raise