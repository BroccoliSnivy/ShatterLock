import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb
from PIL import ImageTk, Image  # ✅ Kept the PIL import

from utils.db_utils import update_entry  # ✅ Function to update data in DB
from utils.secure_operations import encrypt_data, decrypt_data

class EditEntryForm:
    def __init__(self, parent, encryption_key, website, username, password, description, category):
        self.parent = parent
        self.encryption_key = encryption_key  # ✅ Encryption key from main app

        self.website = website
        self.username = username
        self.password = password
        self.description = description
        self.category = category

        self.root_window = self.parent.winfo_toplevel()
        self.create_form()

    def create_form(self):
        """Create the edit entry form window."""
        self.window = tk.Toplevel(self.parent)
        self.window.title("Edit Entry")
        self.window.geometry("700x400")
        self.window.resizable(False, False)

        # Disable the root window while the form is open
        self.root_window.attributes('-disabled', True)
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

        self.window.columnconfigure(1, weight=1)

        # Heading Label
        heading_label = ttk.Label(self.window, text="Edit Entry", font=("Helvetica", 16, "bold"))
        heading_label.grid(row=0, column=0, columnspan=3, pady=(10, 5))

        separator = ttk.Separator(self.window, orient="horizontal")
        separator.grid(row=1, column=0, columnspan=3, sticky="ew", pady=5)

        # Website Field
        ttk.Label(self.window, text="Website Name:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.website_entry = ttk.Entry(self.window)
        self.website_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
        self.website_entry.insert(0, self.website)

        # Username Field
        ttk.Label(self.window, text="Username:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.username_entry = ttk.Entry(self.window)
        self.username_entry.grid(row=3, column=1, padx=10, pady=5, sticky="ew")
        self.username_entry.insert(0, self.username)

        # Password Field
        ttk.Label(self.window, text="Password:").grid(row=4, column=0, padx=10, pady=5, sticky="w")
        self.password_entry = ttk.Entry(self.window, show="*")
        self.password_entry.grid(row=4, column=1, padx=10, pady=5, sticky="ew")
        decrypted_password = decrypt_data(self.password, self.encryption_key)
        self.password_entry.insert(0, decrypted_password)

        # Description Field
        ttk.Label(self.window, text="Description:").grid(row=5, column=0, padx=10, pady=5, sticky="w")
        self.description_entry = tb.Text(self.window, height=4, width=30)
        self.description_entry.grid(row=5, column=1, padx=10, pady=5, sticky="ew")
        self.description_entry.insert("1.0", self.description)

        # Category Selection
        category_label = ttk.Label(self.window, text="Category", font=("Helvetica", 12, "bold"))
        category_label.grid(row=6, column=0, columnspan=3, pady=(10, 5))

        category_frame = tb.Frame(self.window)
        category_frame.grid(row=7, column=0, columnspan=3, pady=5)
        category_frame.columnconfigure((0, 1, 2), weight=1)

        self.category_var = tk.StringVar(value=self.category)
        categories = ["Social Media", "Work", "Shopping", "Security & Tech", "Banking", "Education"]
        for i, category in enumerate(categories):
            row = 0 if i < 3 else 1
            col = i % 3
            ttk.Radiobutton(category_frame, text=category, variable=self.category_var, value=category).grid(row=row, column=col, padx=5, pady=2, sticky="w")

        # Save Changes Button
        self.save_button = tb.Button(self.window, text="Save Changes", bootstyle="success", command=self.save_changes)
        self.save_button.grid(row=8, column=0, columnspan=3, pady=10)

    def save_changes(self):
        """Update the entry in the database."""
        website = self.website_entry.get().strip()
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        description = self.description_entry.get("1.0", "end-1c").strip()
        category = self.category_var.get()

        if website and username and password:
            encrypted_password = encrypt_data(password, self.encryption_key)
            update_entry(self.website, website, username, encrypted_password, description, category)
            self.root_window.attributes('-disabled', False)
            self.window.destroy()
        else:
            print("All fields except description must be filled!")

    def on_close(self):
        """Re-enable the main application window when this form is closed manually."""
        self.root_window.attributes('-disabled', False)
        self.window.destroy()
