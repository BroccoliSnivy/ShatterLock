#The main GUi files of this project
#TTKBootStrap imports 
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import StringVar

#Application customization imports
from PIL import Image, ImageTk
from utils.main_box import MainBox

#OG Tkinter imports
from tkinter import messagebox

#Importing the functional operation files 
from utils.secure_operations import *
from utils.db_utils import *
from utils.password_gen import generate_password
from resources.tooltip import ToolTip

#Importing the file for test run purposes
from getpass import getpass

import os
import json
import random

SETTINGS_FILE = "user_settings.json"

def load_theme():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as file:
            settings = json.load(file)
        return settings.get("theme", "cyborg")
    return "cyborg"

def save_theme(theme):
    with open(SETTINGS_FILE, "w") as file:
        json.dump({"theme" : theme}, file)

class MasterPasswordManager:
    def __init__(self, root):

        #window and appearance customizations
        self.root = root

        self.root.themename = load_theme()

        #Visual Elements
        icon = Image.open('resources/bomber.png')
        icon = ImageTk.PhotoImage(icon)
        root.iconphoto(False, icon)


        #hasing, encryption and other important values (remember to secure this)
        self.der_key = None

        self.db_file = db_file

        self.failed_attempts = 0

        #Database Operations Initialized
        initialize_db()
        master_hash = get_master_hash()
        
        # Check if master password exists
        if master_hash == None:
            self.show_setup_window()
        else:
            self.show_login_window()
        
    
    # def master_password_exists(self):
    #     # Placeholder function to check if the master password exists
    #     # Replace this with actual database verification logic
    #     return False  # Change to True if a master password is already set
    
    #First time login window that asks for master pass
    def show_setup_window(self, title="Master Password Setup"):
        self.root.title(title)
        self.root.geometry("400x350")  # Adjusted height for better spacing
        self.root.resizable(False, False)

        for widget in self.root.winfo_children():
            widget.destroy()

        tb.Label(self.root, text="No existing Master Password Found.\nCreate a Strong Password", justify="center", font=("Arial", 15, "bold")).pack(pady=10)

        self.separator = tb.Separator(self.root, bootstyle="light")
        self.separator.pack(fill="x", pady=10, padx=5)

        tb.Label(self.root, text="Enter new Password").pack(pady=5)

        self.master_entry = tb.Entry(self.root, show="*")
        self.master_entry.pack(pady=5)

        tb.Label(self.root, text="Confirm Password:").pack(pady=5)

        self.confirm_entry = tb.Entry(self.root, show="*")
        self.confirm_entry.pack(pady=5)

        # Add the toggle button **below password fields** but **above the submit button**
        # self.add_password_visibility_toggle_new_user(self.master_entry, self.root)

        self.add_password_controls(root)

        tb.Button(self.root, text="Submit", bootstyle="success-outline", command=self.validate_and_store_password).pack(pady=15)

        # tb.Label(self.root, text="No Master password found.\nThis may be your first use.\nSet new one.", 
        #         font=("Arial", 8, "bold"), bootstyle="light", justify="center").pack(pady=5) 

    #Login window when master pass is already set
    def show_login_window(self, title="Login"):
        self.root.title(title)
        self.root.geometry("300x250")
        self.root.resizable(False, False)
        
        for widget in self.root.winfo_children():
            widget.destroy()

        tb.Label(text="Login", font=("Arial", 20, "bold")).pack(pady=10)

        self.separator = tb.Separator(self.root, bootstyle="light")
        self.separator.pack(fill="x", pady=10, padx=5)

        tb.Label(self.root, text="Enter Master Password:").pack(pady=5)

        self.login_entry = tb.Entry(self.root, show="*")
        self.login_entry.pack(pady=5)

        self.add_password_visibility_toggle_user_login(self.login_entry, self.root)
        
        tb.Button(self.root, text="Login", bootstyle="success-outline", command=self.verify_master_password).pack(pady=15)
    
    def validate_and_store_password(self):

        password = self.master_entry.get()
        confirm_password = self.confirm_entry.get()

        if not password or not confirm_password:
            messagebox.showerror("Error", "Both fields are required!")
            return
        
        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match!")
            return
        
        if len(password) < 12:
            messagebox.showerror("Password must be atleast 12 characters long!")
        
        set_master_password(password)
        # Here you should store the password securely (hash it and save in DB)
        messagebox.showinfo("Success", "Master Password Set Successfully!")
        self.show_login_window()

    def verify_master_password(self):
        password = self.login_entry.get()
        
        verify_flag, self.der_key = verify_password_and_derive_key(get_master_hash(), password)

        if verify_flag:
            messagebox.showinfo("Success", "Login Successful!")
            self.failed_attempts = 0  # Reset on success

            self.show_main_box()

        else:
            self.failed_attempts += 1
            messagebox.showerror("Error", f"Incorrect Password! {10 - self.failed_attempts} attempts left.")
            
            if self.failed_attempts >= 10:
                self.destroy_database()
    
    def get_derived_key(self):
        return self.der_key

    def destroy_database(self):
        if os.path.exists(self.db_file):
            os.remove(self.db_file)  # Delete database file
            messagebox.showwarning("Database Destroyed", "Too many failed attempts! Database deleted.")
        else:
            messagebox.showerror("Error", "Database file not found!")
        
        self.root.destroy()

    def add_password_controls(self, parent):
        """Creates a frame with the visibility toggle button and the password generate button side by side."""

        control_frame = tb.Frame(parent)
        control_frame.pack(pady=5)  # Adjust position as needed

        # Load images once
        if not hasattr(self, "eye_open"):
            try:
                eye_open = Image.open("resources/eye_open.png").resize((20, 20))
                eye_closed = Image.open("resources/eye_closed.png").resize((20, 20))
                self.eye_open = ImageTk.PhotoImage(eye_open)
                self.eye_closed = ImageTk.PhotoImage(eye_closed)
            except Exception as e:
                print("Error loading eye images:", e)
                return  

        # Track password visibility state
        self.password_visible = False  

        # Toggle Button (Column 0)
        toggle_button = tb.Button(control_frame, image=self.eye_closed, bootstyle="danger-outline", width=30)
        toggle_button.grid(row=0, column=0, padx=5)

        ToolTip(toggle_button, text="Password Hidden")


        def toggle_password():
            """Toggle password visibility on each button click."""
            self.password_visible = not self.password_visible  # Switch state

            if self.password_visible:
                self.master_entry.config(show="")
                self.confirm_entry.config(show="")
                toggle_button.config(image=self.eye_open)  # Update button image
            else:
                self.master_entry.config(show="*")
                self.confirm_entry.config(show="*")
                toggle_button.config(image=self.eye_closed)  # Update button image

        toggle_button.config(command=toggle_password)  # Assign function to button click

        # Load images once
        if not hasattr(self, "generate"):
            try:
                generate = Image.open("resources/generate.png").resize((20, 20))
                self.generate = ImageTk.PhotoImage(generate)
            except Exception as e:
                print("Error loading eye images:", e)
                return

        # Generate Password Button (Column 1)
        generate_button = tb.Button(control_frame, image=self.generate, bootstyle="primary-outline", command=self.on_generate_password)
        generate_button.grid(row=0, column=1, padx=5)

        ToolTip(generate_button, text="Generate Password")
    
    def on_generate_password(self):
        """Generates a password and sets it in both password fields."""
        new_password = generate_password()  # Call the password generator function
        self.master_entry.delete(0, "end")
        self.master_entry.insert(0, new_password)
        self.confirm_entry.delete(0, "end")
        self.confirm_entry.insert(0, new_password)
    
    def add_password_visibility_toggle_user_login(self, entry_widget, parent):
        """Adds a separate button below the password field to toggle visibility when held."""

        def show_password(event):
            """Show the password while the button is pressed."""
            self.login_entry.config(show="")
            toggle_button.config(image=self.eye_open)  # Change to open-eye image

        def hide_password(event):
            """Hide the password when the button is released."""
            self.login_entry.config(show="*")
            toggle_button.config(image=self.eye_closed)  # Change to closed-eye image

        if not hasattr(self, "eye_open"):
            try:
                eye_open = Image.open("resources/eye_open.png").resize((20, 20))  
                eye_closed = Image.open("resources/eye_closed.png").resize((20, 20))

                self.eye_open = ImageTk.PhotoImage(eye_open)  
                self.eye_closed = ImageTk.PhotoImage(eye_closed)  

            except Exception as e:
                print("Error loading eye images:", e)
                return  

        # Create the toggle button below the entry field
        toggle_button = tb.Button(parent, image=self.eye_closed, bootstyle="danger-outline", width=30)

        ToolTip(toggle_button, text="Password Hidden")

        toggle_button.bind("<ButtonPress-1>", show_password)  
        toggle_button.bind("<ButtonRelease-1>", hide_password)  

        toggle_button.pack(pady=5)  # Positioned right above Submit button
        
    def show_main_box(self):
        """Function to display the main application UI **after** successful login."""
        self.root.title("ShatterLock - Password Manager")
        self.root.geometry("1200x800")
        self.root.resizable(True, True)
        self.clear_window()

        self.main_app = MainBox(self.root, self.der_key)
        self.main_app.pack(expand=True, fill="both", padx=10, pady=10)
    
    
    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy() 

if __name__ == "__main__":
    theme = load_theme()
    root = tb.Window(themename=theme)  # Change theme if needed
    app = MasterPasswordManager(root)
    root.mainloop()
