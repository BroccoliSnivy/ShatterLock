import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb

from PIL import ImageTk, Image

from utils.db_utils import store_entry  # Function to store data in DB
from utils.secure_operations import encrypt_data
from utils.password_gen import generate_password

class AddEntryForm:
    def __init__(self, master, encryption_key):
        self.master = master
        self.encryption_key = encryption_key  # Get encryption key from the main app
        self.root_window = self.master.winfo_toplevel()  # Get root Tkinter window
        self.create_form()

    def create_form(self):
        """Create the add entry form window."""
        self.window = tk.Toplevel(self.master)
        self.window.title("Add New Entry")
        self.window.geometry("700x400")
        self.window.resizable(False, False)

        # Disable the root window (MainBox's parent) while the form is open
        self.root_window.attributes('-disabled', True)

        # Ensure the main window is re-enabled when this window is closed manually
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

        # Create a grid layout
        self.window.columnconfigure(1, weight=1)  # Allow the second column to expand

        # Heading Label
        heading_label = ttk.Label(self.window, text="Add Entry", font=("Helvetica", 16, "bold"))
        heading_label.grid(row=0, column=0, columnspan=3, pady=(10, 5))

        # Separator
        separator = ttk.Separator(self.window, orient="horizontal")
        separator.grid(row=1, column=0, columnspan=3, sticky="ew", pady=5)

        # Website Field
        ttk.Label(self.window, text="Website Name:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.website_entry = ttk.Entry(self.window)
        self.website_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        # Username Field
        ttk.Label(self.window, text="Username:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.username_entry = ttk.Entry(self.window)
        self.username_entry.grid(row=3, column=1, padx=10, pady=5, sticky="ew")

        # Password Field
        ttk.Label(self.window, text="Password:").grid(row=4, column=0, padx=10, pady=5, sticky="w")
        self.password_entry = ttk.Entry(self.window, show="*")
        self.password_entry.grid(row=4, column=1, padx=10, pady=5, sticky="ew")

        # Password Control Frame (Toggle + Generate + Copy Button)
        control_frame = tb.Frame(self.window)
        control_frame.grid(row=4, column=2, padx=5, pady=5, sticky="w")

        # Load images once
        if not hasattr(self, "eye_open"):
            try:
                eye_open = Image.open("resources/eye_open.png").resize((20, 20))
                eye_closed = Image.open("resources/eye_closed.png").resize((20, 20))
                copy_icon = Image.open("resources/copy.png").resize((20, 20))
                self.eye_open = ImageTk.PhotoImage(eye_open)
                self.eye_closed = ImageTk.PhotoImage(eye_closed)
                self.copy_icon = ImageTk.PhotoImage(copy_icon)
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

        # Load generate button image
        if not hasattr(self, "generate"):
            try:
                generate = Image.open("resources/generate.png").resize((20, 20))
                self.generate = ImageTk.PhotoImage(generate)
            except Exception as e:
                print("Error loading generate image:", e)
                return

        # Generate Password Button
        generate_button = tb.Button(control_frame, image=self.generate, bootstyle="primary-outline", command=self.on_generate_password)
        generate_button.grid(row=0, column=1, padx=5)

        # Copy Password Button
        copy_button = tb.Button(control_frame, image=self.copy_icon, bootstyle="info-outline", command=self.copy_password)
        copy_button.grid(row=0, column=2, padx=5)

        # Description Field
        ttk.Label(self.window, text="Description:").grid(row=5, column=0, padx=10, pady=5, sticky="w")
        self.description_entry = tb.Text(self.window, height=4, width=30)
        self.description_entry.grid(row=5, column=1, padx=10, pady=5, sticky="ew")

        # Category Heading
        category_label = ttk.Label(self.window, text="Category", font=("Helvetica", 12, "bold"))
        category_label.grid(row=6, column=0, columnspan=3, pady=(10, 5))

        # Category Selection Frame
        category_frame = tb.Frame(self.window)
        category_frame.grid(row=7, column=0, columnspan=3, pady=5)
        category_frame.columnconfigure((0, 1, 2), weight=1)  # Make columns equal width

        self.category_var = tk.StringVar(value="Social Media")
        categories = ["Social Media", "Work", "Shopping", "Security & Tech", "Banking", "Education"]

        # Create category buttons in two rows
        for i, category in enumerate(categories):
            row = 0 if i < 3 else 1  # First three in row 0, next in row 1
            col = i % 3  # Position in row
            ttk.Radiobutton(category_frame, text=category, variable=self.category_var, value=category).grid(row=row, column=col, padx=5, pady=2, sticky="w")

        # Submit Button
        self.submit_button = tb.Button(self.window, text="Submit", bootstyle="success", command=self.submit_entry)
        self.submit_button.grid(row=8, column=0, columnspan=3, pady=10)

    def copy_password(self):
        """Copies the password from the entry field to the clipboard."""
        password = self.password_entry.get()
        if password:
            self.window.clipboard_clear()
            self.window.clipboard_append(password)
            self.window.update()  # Keeps the clipboard data available


    def on_generate_password(self):
        """Generates a password and sets it in the password field."""
        new_password = generate_password()  # Call the password generator function
        self.password_entry.delete(0, "end")
        self.password_entry.insert(0, new_password) 

    def submit_entry(self):
        """Store the new entry in the database."""
        website = self.website_entry.get().strip()
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        description = self.description_entry.get("1.0", "end-1c").strip()
        category = self.category_var.get()

        if website and username and password:
            encrypted_password = encrypt_data(password, self.encryption_key)  # Encrypt password
            store_entry(website, username, encrypted_password, description, category, self.encryption_key)  # Store in DB

            # Re-enable MainBox's root window and close the form
            self.root_window.attributes('-disabled', False)
            self.window.destroy()
        else:
            print("All fields except description must be filled!")  # Replace with a popup message if needed

    def on_close(self):
        """Re-enable the main application window when this form is closed manually."""
        self.root_window.attributes('-disabled', False)
        self.window.destroy()
