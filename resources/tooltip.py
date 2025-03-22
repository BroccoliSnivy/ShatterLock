import tkinter as tk

class ToolTip:
    """Custom hover tooltip for Tkinter widgets with full styling control."""

    def __init__(self, widget, text, bg="#333", fg="white", font=("Arial", 10, "bold"), delay=500):
        """
        :param widget: Tkinter widget where the tooltip will be attached
        :param text: Tooltip text
        :param bg: Background color (default: dark gray)
        :param fg: Text color (default: white)
        :param font: Font style for tooltip text
        :param delay: Delay before showing tooltip (default: 200ms)
        """
        self.widget = widget
        self.text = text
        self.bg = bg
        self.fg = fg
        self.font = font
        self.delay = delay
        self.tooltip = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        """Display tooltip near the widget."""
        if self.tooltip:
            return

        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)  # Remove window decorations
        self.tooltip.configure(bg=self.bg)

        label = tk.Label(self.tooltip, text=self.text, bg=self.bg, fg=self.fg, font=self.font, padx=5, pady=3)
        label.pack()

        # Positioning
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 20  # Adjust X position
        y += self.widget.winfo_rooty() + 30  # Adjust Y position
        self.tooltip.wm_geometry(f"+{x}+{y}")

    def hide_tooltip(self, event=None):
        """Destroy the tooltip when mouse leaves the widget."""
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None
