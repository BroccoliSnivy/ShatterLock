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

def get_entry_from_db(website, username):
    """Retrieve a stored entry from the database based on website and username."""
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT website, username, encrypted_password, description, category 
            FROM stored_passwords 
            WHERE website = ? AND username = ?
        """, (website, username))
        entry = cursor.fetchone()

    return entry  # Returns (website, username, encrypted_password, description, category) OR None

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

def store_entry(website, username, encrypted_password, description, category):
    """Store encrypted password along with description and category."""
    if not encrypted_password:
        raise ValueError("Encrypted password cannot be empty!")
    
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO stored_passwords (website, username, encrypted_password, description, category) 
            VALUES (?, ?, ?, ?, ?)
        """, (website, username, encrypted_password, description, category))
        conn.commit()

def retrieve_passwords_with_decryption(key):
    """Retrieve and decrypt stored passwords when needed."""
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT website, username, encrypted_password, description, category FROM stored_passwords")
        records = cursor.fetchall()

        decrypted_records = []
        for website, username, encrypted_password, description, category in records:
            print(f"Decrypting - Encrypted Password: {encrypted_password[:30]}...")  # Debug print

            decrypted_password = decrypt_data(encrypted_password, key)

            if not decrypted_password:
                print("ERROR: Decryption failed.")

            decrypted_records.append((website, username, decrypted_password, description, category))

        return decrypted_records

def retrieve_passwords_for_display():
    """Retrieve stored entries without decrypting passwords for UI display."""
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT website, username, description, category FROM stored_passwords")
        records = cursor.fetchall()

        masked_records = [(website, username, '*' * 16, description, category) for website, username, description, category in records]
        return masked_records

# def update_entry(old_website, new_website, username, encrypted_password, description, category):
#     """Update an existing entry in the database."""
#     with sqlite3.connect(db_file) as conn:
#         cursor = conn.cursor()
#         cursor.execute("""
#             UPDATE stored_passwords 
#             SET website = ?, username = ?, encrypted_password = ?, description = ?, category = ?
#             WHERE website = ?
#         """, (new_website, username, encrypted_password, description, category, old_website))
#         conn.commit()

# def update_entry(old_website, new_website, username, encrypted_password, description, category):
#     """Update an existing entry in the database."""
#     with sqlite3.connect(db_file) as conn:
#         cursor = conn.cursor()
#         cursor.execute("""
#             UPDATE stored_passwords 
#             SET website = ?, username = ?, encrypted_password = ?, description = ?, category = ?
#             WHERE website = ? AND username = ?
#         """, (new_website, username, encrypted_password, description, category, old_website, username))
#         conn.commit()

def update_entry(old_website, new_website, username, password, description, category, key):
    """Update an existing entry in the database."""

    # Encrypt the password inside this function to ensure consistency
    encrypted_password = encrypt_data(password, key)

    if not encrypted_password:
        print("ERROR: Encryption failed. Password not updated.")
        return

    # print(f"🔸 Updating entry - Encrypted Password: {encrypted_password[:30]}...")  # Debug print

    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE stored_passwords 
            SET website = ?, username = ?, encrypted_password = ?, description = ?, category = ?
            WHERE website = ? AND username = ?
        """, (new_website, username, encrypted_password, description, category, old_website, username))
        conn.commit()

def store_entry(website, username, password, description, category, key):
    """Encrypt and store password with description and category."""
    encrypted_password = encrypt_data(password, key)

    if not encrypted_password:  
        print("ERROR: Encryption failed. Password not stored.")
        return

    print(f"Storing entry - Encrypted Password: {encrypted_password[:30]}...")  # Debug print

    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO stored_passwords (website, username, encrypted_password, description, category) VALUES (?, ?, ?, ?, ?)", 
                       (website, username, encrypted_password, description, category))
        conn.commit()

def delete_entry(website, username):
    """
    Deletes an entry from the database using website and username as identifiers.

    Args:
        website (str): The website name of the entry.
        username (str): The username associated with the entry.
    """
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        # Execute delete query
        cursor.execute("DELETE FROM stored_passwords WHERE website=? AND username=?", (website, username))

        conn.commit()
        conn.close()
        print(f"Entry deleted: {website} ({username})")
    except sqlite3.Error as e:
        print("Error deleting entry:", e)

def fetch_all_entries():
    """Fetch all stored entries for displaying in the Treeview."""
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT website, username, description, category FROM stored_passwords")
        return cursor.fetchall()  # Returns a list of tuples

def get_entries_by_category(category):
    """Fetch entries based on the selected category."""
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    if category == "All":
        cursor.execute("SELECT * FROM stored_passwords ORDER BY website ASC")  # Fetch all
    else:
        cursor.execute("SELECT * FROM stored_passwords WHERE category = ? ORDER BY website ASC", (category,))
    
    results = cursor.fetchall()
    conn.close()
    
    return results
