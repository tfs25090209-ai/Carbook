"""Base frame widget for consistent styling."""

import customtkinter as ctk

from theme.colors import *


class BaseFrame(ctk.CTkFrame):
    """Base frame with consistent styling."""

    def __init__(self, master, **kwargs):
        # Default styling — transparent for layering
        kwargs.setdefault("fg_color", "transparent")
        kwargs.setdefault("corner_radius", 0)

        super().__init__(master, **kwargs)

    def clear(self):
        """Clear all widgets from the frame."""
        for widget in self.winfo_children():
            widget.destroy()

    def set_card_style(self):
        """Switch to card styling with subtle border."""
        self.configure(
            fg_color=BG_CARD,
            corner_radius=CARD_RADIUS,
            border_color=BORDER,
            border_width=1
        )