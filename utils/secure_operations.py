from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from passlib.hash import pbkdf2_sha256
import hashlib
import os
import base64
import binascii

# AES Key Size (32 bytes for AES-256)
AES_KEY_SIZE = 32
PBKDF2_ITERATIONS = 100000
SALT_SIZE = 16  # Recommended size for PBKDF2 salt
IV_SIZE = 16  # AES CBC IV size

def encrypt_data(plaintext, key):
    """Encrypt data using AES CBC mode with proper key and IV handling."""
    if not plaintext:
        raise ValueError("Encryption error: Empty plaintext.")

    if not key or len(key) != AES_KEY_SIZE:
        raise ValueError(f"Encryption error: Invalid key length ({len(key) if key else 'None'} bytes).")

    if isinstance(plaintext, str):
        plaintext = plaintext.encode('utf-8')

    iv = os.urandom(IV_SIZE)  # Generate a random IV
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ciphertext = cipher.encrypt(pad(plaintext, AES.block_size))

    encrypted_b64 = base64.b64encode(iv + ciphertext).decode('utf-8')

    # Debugging
    print(f"Encryption Successful - Ciphertext Length: {len(encrypted_b64)}")

    return encrypted_b64

def decrypt_data(encrypted_data, key):
    """Decrypt AES-CBC encrypted data and remove PKCS7 padding."""
    try:
        encrypted_data_bytes = base64.b64decode(encrypted_data)
        iv = encrypted_data_bytes[:16]
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted_padded = cipher.decrypt(encrypted_data_bytes[16:])
        
        # Remove PKCS7 padding
        pad_length = decrypted_padded[-1]
        decrypted_data = decrypted_padded[:-pad_length].decode("utf-8")

        return decrypted_data
    except Exception:
        return encrypted_data

def verify_password_and_derive_key(stored_hash, entered_password):
    """Verify the master password and derive a 32-byte encryption key."""
    if pbkdf2_sha256.verify(entered_password, stored_hash):
        # Generate a 32-byte key
        key = hashlib.pbkdf2_hmac('sha256', entered_password.encode('utf-8'), stored_hash.encode(), PBKDF2_ITERATIONS, AES_KEY_SIZE)
        return True, key
    return False, None


def hash_master_password(master_password):
    """Hash the master password using PBKDF2 with a random salt."""
    return pbkdf2_sha256.using(rounds=PBKDF2_ITERATIONS, salt_size=SALT_SIZE).hash(master_password)
