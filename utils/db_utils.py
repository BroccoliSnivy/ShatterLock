import sqlite3
from passlib.hash import pbkdf2_sha256
from utils.secure_operations import encrypt_data, decrypt_data

db_file = "password_database.db"

def initialize_db():
    """Create tables if they do not exist."""
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS master (
                            id INTEGER PRIMARY KEY, 
                            password_hash TEXT NOT NULL
                         )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS stored_passwords (
                            id INTEGER PRIMARY KEY, 
                            website TEXT NOT NULL, 
                            username TEXT NOT NULL, 
                            encrypted_password BLOB NOT NULL,
                            description TEXT,
                            category TEXT NOT NULL
                         )''')
        conn.commit()

def get_master_hash():
    """Retrieve the stored master password hash."""
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash FROM master LIMIT 1")
        result = cursor.fetchone()
        return result[0] if result else None

def set_master_password(password):
    """Hash and store the master password."""
    password_hash = pbkdf2_sha256.hash(password)
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO master (password_hash) VALUES (?)", (password_hash,))
        conn.commit()

def verify_master_password(password):
    """Verify entered master password against stored hash."""
    stored_hash = get_master_hash()
    return stored_hash and pbkdf2_sha256.verify(password, stored_hash)

def store_entry(website, username, password, description, category, key):
    """Encrypt and store password with description and category."""
    encrypted_password = encrypt_data(password, key)
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO stored_passwords (website, username, encrypted_password, description, category) VALUES (?, ?, ?, ?, ?)", 
                       (website, username, encrypted_password, description, category))
        conn.commit()

# def retrieve_passwords(key):
#     """Retrieve and decrypt stored passwords with description and category."""
#     with sqlite3.connect(db_file) as conn:
#         cursor = conn.cursor()
#         cursor.execute("SELECT website, username, encrypted_password, description, category FROM stored_passwords")
#         records = cursor.fetchall()
        
#         decrypted_records = []
#         for website, username, encrypted_password, description, category in records:
#             decrypted_password = decrypt_data(encrypted_password, key)
#             decrypted_records.append((website, username, decrypted_password, description, category))
        
#         return decrypted_records

def retrieve_passwords_with_decryption(key):
    """Retrieve and decrypt stored passwords when needed."""
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT website, username, encrypted_password, description, category FROM stored_passwords")
        records = cursor.fetchall()

        decrypted_records = []
        for website, username, encrypted_password, description, category in records:
            decrypted_password = decrypt_data(encrypted_password, key)
            decrypted_records.append((website, username, decrypted_password, description, category))

        return decrypted_records

def retrieve_passwords_for_display():
    """Retrieve stored entries without decrypting passwords for UI display."""
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT website, username, description, category FROM stored_passwords")
        records = cursor.fetchall()

        masked_records = []
        for website, username, description, category in records:
            masked_password = '*' * 16  # Masked password for display
            masked_records.append((website, username, masked_password, description, category))

        return masked_records

def update_entry(website, username, new_password, new_description, new_category, key):
    """Update an existing entry's password, description, and category."""
    encrypted_password = encrypt_data(new_password, key)
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute('''UPDATE stored_passwords 
                          SET encrypted_password = ?, description = ?, category = ? 
                          WHERE website = ? AND username = ?''',
                       (encrypted_password, new_description, new_category, website, username))
        conn.commit()