import sqlite3

db_file = "password_database.db"  # Update this path if needed

def check_entries():
    """Retrieve and display all stored entries from the database."""
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, website, username, encrypted_password, description, category FROM stored_passwords")
        records = cursor.fetchall()
        
        if not records:
            print("No entries found in the database.")
        else:
            print("Stored Entries:")
            for record in records:
                print(f"ID: {record[0]}, Website: {record[1]}, Username: {record[2]}, "
                      f"Encrypted Password: {record[3]}, Description: {record[4]}, Category: {record[5]}")

# Run the check
if __name__ == "__main__":
    check_entries()
