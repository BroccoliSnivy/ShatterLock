from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from passlib.hash import pbkdf2_sha256
import hashlib
import os
import base64

# AES Key Size (32 bytes for AES-256)
AES_KEY_SIZE = 32
PBKDF2_ITERATIONS = 100000
SALT_SIZE = 16  # Recommended size for PBKDF2 salt
IV_SIZE = 16  # AES CBC IV size

def encrypt_data(plaintext, key):
    """Encrypt data using AES CBC mode with a securely generated IV."""
    iv = os.urandom(IV_SIZE)  # Securely generate IV
    cipher = AES.new(key, AES.MODE_CBC, iv)
    
    if isinstance(plaintext, str):
        plaintext = plaintext.encode('utf-8')

    ciphertext = cipher.encrypt(pad(plaintext, AES.block_size))
    return iv + ciphertext  # Store IV + Encrypted Data

def decrypt_data(ciphertext, key):
    """Decrypt data using AES CBC mode, ensuring correct IV handling."""
    try:
        if not ciphertext:
            print("Decryption error: Empty ciphertext.")
            return ""

        # If the ciphertext is a string, decode it from Base64
        if isinstance(ciphertext, str):
            ciphertext = base64.b64decode(ciphertext)

        if len(ciphertext) < 16:
            print("Decryption error: Invalid ciphertext format.")
            return ""

        iv = ciphertext[:16]  # Extract the first 16 bytes as IV
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted_data = unpad(cipher.decrypt(ciphertext[16:]), AES.block_size)

        return decrypted_data.decode('utf-8', errors='replace')

    except (ValueError, KeyError, TypeError) as e:
        print(f"Decryption error: {e}")
        return ""

# def decrypt_data(ciphertext, key):
#     """Decrypt data using AES CBC mode, handling potential errors."""
#     try:
#         iv = ciphertext[:16]  # Extract IV (first 16 bytes)
#         cipher = AES.new(key, AES.MODE_CBC, iv)
#         decrypted_data = unpad(cipher.decrypt(ciphertext[16:]), AES.block_size)

#         # Ensure the result is valid UTF-8 before returning
#         return decrypted_data.decode('utf-8', errors='replace')  # Replace invalid bytes
        
#     except (ValueError, KeyError) as e:
#         print(f"Decryption error: {e}")
#         return None 

def hash_master_password(master_password):
    """Hash the master password using PBKDF2 with a random salt."""
    return pbkdf2_sha256.using(rounds=PBKDF2_ITERATIONS, salt_size=SALT_SIZE).hash(master_password)

def verify_password_and_derive_key(stored_hash, entered_password):
    """
    Verify the master password and derive an encryption key.
    
    If the password is correct, derive a key using PBKDF2 with the hash as the salt.
    """
    if pbkdf2_sha256.verify(entered_password, stored_hash):
        salt = stored_hash.encode()[:SALT_SIZE]  # Extract pseudo-salt (improve if you store actual salt separately)
        key = hashlib.pbkdf2_hmac('sha256', entered_password.encode('utf-8'), salt, PBKDF2_ITERATIONS, dklen=AES_KEY_SIZE)
        return True, key
    return False, None
