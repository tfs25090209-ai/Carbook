"""Placeholder page for navigation items."""

import customtkinter as ctk
from ui.pages.base_page import BasePage
from theme.colors import *


class PlaceholderPage(BasePage):
    """Placeholder page for future implementation."""

    def __init__(self, master, app, title: str, **kwargs):
        self.title_text = title
        super().__init__(master, app, **kwargs)
        self._setup_ui()

    def _setup_ui(self):
        """Setup the placeholder page UI using grid throughout."""
        # Let this page expand via grid (it is placed with grid by the app)
        self.grid_rowconfigure(0, weight=0)  # title row
        self.grid_rowconfigure(1, weight=0)  # subtitle row
        self.grid_rowconfigure(2, weight=1)  # card (expands)
        self.grid_columnconfigure(0, weight=1)

        # Title
        title = ctk.CTkLabel(
            self,
            text=self.title_text,
            font=ctk.CTkFont(size=28, weight="bold", family="Helvetica"),
            text_color=TEXT_PRIMARY
        )
        title.grid(row=0, column=0, sticky="w", padx=PAGE_PAD_X, pady=(PAGE_PAD_Y, 10))

        # Subtitle
        subtitle = ctk.CTkLabel(
            self,
            text="Coming soon...",
            font=ctk.CTkFont(size=14, family="Helvetica"),
            text_color=TEXT_SECONDARY
        )
        subtitle.grid(row=1, column=0, sticky="w", padx=PAGE_PAD_X, pady=(0, 20))

        # Placeholder card — fills remaining space
        card = ctk.CTkFrame(
            self,
            fg_color=BG_CARD,
            corner_radius=CARD_RADIUS,
            border_color=BORDER,
            border_width=1
        )
        card.grid(row=2, column=0, sticky="nsew", padx=PAGE_PAD_X, pady=(0, 30))
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(0, weight=1)
        card.grid_rowconfigure(1, weight=0)
        card.grid_rowconfigure(2, weight=1)

        # Elegant placeholder icon — centred vertically
        icon_label = ctk.CTkLabel(
            card,
            text="◈",
            font=ctk.CTkFont(size=48),
            text_color=BORDER_LIGHT
        )
        icon_label.grid(row=0, column=0, sticky="s", pady=(40, 10))

        placeholder_label = ctk.CTkLabel(
            card,
            text=f"{self.title_text}",
            font=ctk.CTkFont(size=16, family="Helvetica"),
            text_color=TEXT_MUTED
        )
        placeholder_label.grid(row=1, column=0)