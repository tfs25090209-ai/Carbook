"""Base page class for all application pages."""

import customtkinter as ctk

from theme.colors import BG_MEDIUM


class BasePage(ctk.CTkFrame):
    """Base class for all pages in the application."""

    def __init__(self, master, app, **kwargs):
        kwargs.setdefault("fg_color", BG_MEDIUM)
        super().__init__(master, **kwargs)

        self.app = app

    def on_show(self):
        """Called when the page is shown."""
        pass

    def on_hide(self):
        """Called when the page is hidden."""
        pass
