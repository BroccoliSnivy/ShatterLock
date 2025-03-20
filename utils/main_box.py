import ttkbootstrap as tb
from tkinter import ttk
import json
import os
from utils.db_utils import db_file, retrieve_passwords_for_display
from utils.secure_operations import decrypt_data
from user_settings.user_settings import save_user_settings, load_user_settings
from utils.entry_manager import AddEntryForm
from utils.edit_entry_manager import EditEntryForm

class MainBox(tb.Frame):
    def __init__(self, parent, derived_key):
        super().__init__(parent)
        self.pack(expand=True, fill="both")
        self.style = tb.Style()
        self.available_themes = self.style.theme_names()
        self.current_theme = load_user_settings().get("theme", self.available_themes[0])
        self.style.theme_use(self.current_theme)
        self.create_widgets()
        self.load_entries()

        self.der_key = derived_key

    def create_widgets(self):
        self.columnconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)

        # ===== Top Bar (Header) =====
        top_bar = tb.Frame(self)
        top_bar.grid(row=0, column=0, columnspan=2, sticky="ew")
        tb.Label(top_bar, text="ShatterLock - Password Manager", font=("Arial", 25, "bold"), bootstyle="").pack(side="left", padx=10, pady=10)

        # Theme Menu Button
        self.theme_menu_button = tb.Menubutton(top_bar, text="Change Theme", bootstyle="warning-outline")
        self.theme_menu_button.pack(side="right", padx=10, pady=10)

        # Dropdown menu
        self.theme_menu = tb.Menu(self.theme_menu_button, tearoff=False)
        self.theme_menu_button["menu"] = self.theme_menu

        # Add theme options to menu
        for theme in self.available_themes:
            self.theme_menu.add_command(label=theme, command=lambda t=theme: self.change_theme(t))

        # ===== Separator (Below Top Bar) =====
        ttk.Separator(self, orient="horizontal", bootstyle="light").grid(row=1, column=0, columnspan=2, sticky="ew", pady=5)

        # ===== Sidebar (Filter Panel) =====
        sidebar = tb.Labelframe(self, text="Categories", bootstyle="light")
        sidebar.grid(row=2, column=0, sticky="ns", padx=5)
        tb.Button(sidebar, text="All", bootstyle="secondary-outline", command=self.filter_all).pack(fill="x", padx=10, pady=5)
        tb.Button(sidebar, text="Social Media", bootstyle="primary-outline", command=self.filter_social).pack(fill="x", padx=10, pady=5)
        tb.Button(sidebar, text="Work", bootstyle="danger-outline", command=self.filter_work).pack(fill="x", padx=10, pady=5)
        tb.Button(sidebar, text="Shopping", bootstyle="warning-outline", command=self.filter_work).pack(fill="x", padx=10, pady=5)
        tb.Button(sidebar, text="Security & Tech", bootstyle="info-outline", command=self.filter_work).pack(fill="x", padx=10, pady=5)
        tb.Button(sidebar, text="Banking", bootstyle="success-outline", command=self.filter_banking).pack(fill="x", padx=10, pady=5)

        # ===== Main Content (Treeview) =====
        content_frame = tb.Labelframe(self, text=f"{db_file}", bootstyle="light")
        content_frame.grid(row=2, column=1, sticky="nsew", padx=5)

        self.rowconfigure(2, weight=1)
        self.columnconfigure(1, weight=1)
        content_frame.rowconfigure(0, weight=1)
        content_frame.columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(content_frame, columns=("Site", "Username", "Password", "Description"), show="headings", height=10)

        self.tree.heading("Site", text="Website / App")
        self.tree.heading("Username", text="Username / Email")
        self.tree.heading("Password", text="Password")
        self.tree.heading("Description", text="Description")

        self.tree.column("#0", width=0, stretch=False)
        self.tree.column("Site", width=100, anchor="center", stretch=True)
        self.tree.column("Username", width=100, anchor="center", stretch=True)
        self.tree.column("Password", width=100, anchor="center", stretch=True)
        self.tree.column("Description", width=200, anchor="center", stretch=True)

        y_scroll = ttk.Scrollbar(content_frame, bootstyle="info-round", orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=y_scroll.set)

        self.tree.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        y_scroll.grid(row=0, column=1, sticky="ns")

        self.tree.bind("<Double-1>", self.on_double_click)

        # ===== Bottom Buttons =====
        button_frame = tb.Frame(self)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)

        tb.Button(button_frame, text="Add Entry", bootstyle="success", command=self.add_entry).pack(side="left", padx=10)
        tb.Button(button_frame, text="Edit Entry", bootstyle="warning", command=self.edit_entry).pack(side="left", padx=10)
        tb.Button(button_frame, text="Delete Entry", bootstyle="danger", command=self.delete_entry).pack(side="left", padx=10)
    
    def load_entries(self):
        """Load all entries from the database and display them in the Treeview."""
        self.tree.delete(*self.tree.get_children())  # Clear existing entries

        entries = retrieve_passwords_for_display()  # Fetch entries from DB

        for entry in entries:
            website, username, decrypted_password, description, category = entry
            self.tree.insert("", "end", values=(website, username, decrypted_password, description))

    def on_double_click(self, event):
        """Opens the edit entry form when an entry in the Treeview is double-clicked."""
        selected_item = self.tree.selection()

        if not selected_item:
            return  # No item selected, exit function

        item_data = self.tree.item(selected_item)
        values = item_data["values"]

        # Ensure the values list has at least 5 elements (avoid IndexError)
        website = values[0] if len(values) > 0 else ""
        username = values[1] if len(values) > 1 else ""
        encrypted_password = values[2] if len(values) > 2 else ""
        description = values[3] if len(values) > 3 else ""
        category = values[4] if len(values) > 4 else ""

        # Decrypt password only if it's present
        decrypted_password = decrypt_data(encrypted_password, self.der_key) if encrypted_password else ""

        # Open Edit Entry Form (even if some fields are missing)
        edit_form = EditEntryForm(self, self.der_key, website, username, decrypted_password, description, category)

    def change_theme(self, theme_name):
        self.style.theme_use(theme_name)
        save_user_settings({"theme": theme_name})

    def filter_all(self):
        print("Showing All Entries")

    def filter_social(self):
        print("Filtering Social Media")

    def filter_work(self):
        print("Filtering Work Entries")

    def filter_banking(self):
        print("Filtering Banking Entries")

    def add_entry(self):
        form = AddEntryForm(self, self.der_key)
        self.wait_window(form.window)
        self.load_entries()

    def edit_entry(self):
        print("Edit Entry Clicked")

    def delete_entry(self):
        print("Delete Entry Clicked")
