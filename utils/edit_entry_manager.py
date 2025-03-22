import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb
from PIL import ImageTk, Image  # ✅ Kept the PIL import

from utils.db_utils import update_entry, delete_entry  # ✅ Added delete_entry import
from utils.secure_operations import encrypt_data, decrypt_data
from utils.password_gen import generate_password  # ✅ Import password generator function

class EditEntryForm:
    def __init__(self, parent, encryption_key, website, username, password, description, category, treeview):
        self.parent = parent
        self.encryption_key = encryption_key
        self.website = website
        self.username = username
        self.password = password
        self.description = description
        self.category = category
        self.treeview = treeview  # ✅ Store the Treeview reference

        self.root_window = self.parent.winfo_toplevel()  # ✅ Get the root window
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

        # Password Control Frame (Toggle + Generate + Copy Button)
        control_frame = tb.Frame(self.window)
        control_frame.grid(row=4, column=2, padx=5, pady=5, sticky="w")

        # Load images once
        if not hasattr(self, "eye_open"):
            try:
                eye_open = Image.open("resources/eye_open.png").resize((20, 20))
                eye_closed = Image.open("resources/eye_closed.png").resize((20, 20))
                copy_icon = Image.open("resources/copy.png").resize((20, 20))
                generate_icon = Image.open("resources/generate.png").resize((20, 20))

                self.eye_open = ImageTk.PhotoImage(eye_open)
                self.eye_closed = ImageTk.PhotoImage(eye_closed)
                self.copy_icon = ImageTk.PhotoImage(copy_icon)
                self.generate_icon = ImageTk.PhotoImage(generate_icon)
            except Exception as e:
                print("Error loading images:", e)
                return

        # Track password visibility state
        self.password_visible = False

        # Toggle Button
        toggle_button = tb.Button(control_frame, image=self.eye_closed, bootstyle="danger-outline", width=30)
        toggle_button.grid(row=0, column=0, padx=5)

        def toggle_password():
            """Toggle password visibility on each button click."""
            self.password_visible = not self.password_visible
            if self.password_visible:
                self.password_entry.config(show="")
                toggle_button.config(image=self.eye_open)
            else:
                self.password_entry.config(show="*")
                toggle_button.config(image=self.eye_closed)

        toggle_button.config(command=toggle_password)

        # Generate Password Button
        generate_button = tb.Button(control_frame, image=self.generate_icon, bootstyle="primary-outline", command=self.on_generate_password)
        generate_button.grid(row=0, column=1, padx=5)

        # Copy Password Button
        copy_button = tb.Button(control_frame, image=self.copy_icon, bootstyle="info-outline", command=self.copy_password)
        copy_button.grid(row=0, column=2, padx=5)

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

        # Button Frame (Save & Delete)
        button_frame = tb.Frame(self.window)
        button_frame.grid(row=8, column=0, columnspan=3, pady=10)

        # Save Changes Button
        save_button = tb.Button(button_frame, text="Save Changes", bootstyle="success", command=self.save_changes)
        save_button.pack(side="left", padx=10)

        # Delete Entry Button
        delete_button = tb.Button(button_frame, text="Delete Entry", bootstyle="danger", command=self.delete_entry)
        delete_button.pack(side="left", padx=10)

    def delete_entry(self):
        """Deletes the entry from the database."""
        delete_entry(self.website, self.username)  # ✅ Call the database function to delete entry
        self.root_window.attributes('-disabled', False)
        self.window.destroy()
        self.refresh_treeview()

    def copy_password(self):
        """Copies the password from the entry field to the clipboard."""
        password = self.password_entry.get()
        if password:
            self.window.clipboard_clear()
            self.window.clipboard_append(password)
            self.window.update()

    def on_generate_password(self):
        """Generates a password and sets it in the password field."""
        new_password = generate_password()
        self.password_entry.delete(0, "end")
        self.password_entry.insert(0, new_password)

    # def save_changes(self):
    #     """Update the entry in the database."""
    #     encrypted_password = encrypt_data(self.password_entry.get().strip(), self.encryption_key)

    #     update_entry(
    #         self.website,  # old_website
    #         self.website_entry.get().strip(),  # new_website
    #         self.username_entry.get().strip(),
    #         encrypted_password,
    #         self.description_entry.get("1.0", "end-1c").strip(),
    #         self.category_var.get()
    #     )

    #     self.root_window.attributes('-disabled', False)
    #     self.window.destroy()
    #     self.refresh_treeview()

    def save_changes(self):
        """Update the entry in the database."""
        plain_password = self.password_entry.get().strip()
        encrypted_password = encrypt_data(plain_password, self.encryption_key)

        if not encrypted_password:
            print("ERROR: Encryption failed, cannot update the database.")  # Debugging message
            return  # Stop execution if encryption fails

        print(f"🔹 Encrypted Password Before Storing: {encrypted_password[:30]}...")  # Debugging print

        update_entry(
            self.website,  # old_website
            self.website_entry.get().strip(),  # new_website
            self.username_entry.get().strip(),
            encrypted_password,
            self.description_entry.get("1.0", "end-1c").strip(),
            self.category_var.get(),
            self.encryption_key
        )

        self.root_window.attributes('-disabled', False)
        self.window.destroy()
        self.refresh_treeview()

    def on_close(self):
        """Re-enable the main application window when this form is closed manually."""
        self.parent.attributes('-disabled', False)  # Re-enable the main window
        self.window.destroy()

    def refresh_treeview(self):
        """Refresh the Treeview to display updated data."""
        for item in self.treeview.get_children():
            self.treeview.delete(item)
        self.parent.load_entries()
