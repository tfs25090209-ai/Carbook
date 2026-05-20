"""Sidebar navigation widget."""

import customtkinter as ctk
from typing import Callable, Dict, List

from theme.colors import *
from theme.typography import font_heading_sm, font_body_secondary, font_button


class Sidebar(ctk.CTkFrame):
    """Sidebar navigation component."""

    def __init__(
        self,
        master,
        items: List[Dict[str, str]],
        on_select: Callable[[str], None],
        **kwargs
    ):
        kwargs.setdefault("fg_color", SIDEBAR_BG)
        kwargs.setdefault("corner_radius", 0)
        kwargs.setdefault("width", 240)

        super().__init__(master, **kwargs)

        self.items = items
        self.on_select = on_select
        self.buttons: Dict[str, ctk.CTkButton] = {}
        self.accents: Dict[str, ctk.CTkFrame] = {}
        self.active_item = None
        self.icons = {
            "dashboard": "▦",
            "browse_cars": "⟐",
            "my_bookings": "⌚",
            "profile": "◍",
            "logout": "↪",
        }

        self.pack_propagate(False)
        self.configure(width=240)

        self._setup_ui()

    def _setup_ui(self):
        """Setup the sidebar UI components."""
        brand_frame = ctk.CTkFrame(self, fg_color="transparent")
        brand_frame.pack(fill="x", pady=(24, 16), padx=20)

        title_label = ctk.CTkLabel(
            brand_frame,
            text="LUXURYDRIVE",
            font=font_heading_sm(bold=True, size=17),
            text_color=PRIMARY
        )
        title_label.pack(anchor="w")

        subtitle_label = ctk.CTkLabel(
            brand_frame,
            text="Premium Collection",
            font=font_body_secondary(size=12),
            text_color=TEXT_MUTED
        )
        subtitle_label.pack(anchor="w", pady=(2, 0))

        separator = ctk.CTkFrame(self, fg_color=BORDER, height=1)
        separator.pack(fill="x", padx=16, pady=(0, 16))

        for item in self.items:
            self._create_nav_button(item)

    def _create_nav_button(self, item: Dict[str, str]):
        """Create a navigation button with a left accent bar."""
        row = ctk.CTkFrame(self, fg_color="transparent", height=46)
        row.pack(fill="x", padx=12, pady=(24, 2) if item["id"] == "logout" else 2)
        row.pack_propagate(False)

        accent = ctk.CTkFrame(row, fg_color="transparent", width=3, corner_radius=0)
        accent.pack(side="left", fill="y")
        accent.pack_propagate(False)

        btn = ctk.CTkButton(
            row,
            text=f"  {self.icons.get(item['id'], '•')}  {item['label']}",
            fg_color="transparent",
            text_color=TEXT_SECONDARY,
            hover_color=SIDEBAR_HOVER,
            anchor="w",
            height=46,
            corner_radius=6,
            font=font_button(size=12),
            command=lambda: self._on_item_click(item)
        )
        btn.pack(side="left", fill="x", expand=True)

        self.buttons[item["id"]] = btn
        self.accents[item["id"]] = accent

    def _on_item_click(self, item: Dict[str, str]):
        """Handle item click."""
        if self.active_item:
            self.buttons[self.active_item].configure(
                fg_color="transparent",
                text_color=TEXT_SECONDARY
            )
            self.accents[self.active_item].configure(fg_color="transparent")

        self.active_item = item["id"]
        self.buttons[item["id"]].configure(
            fg_color=SIDEBAR_ACTIVE,
            text_color=SIDEBAR_ACTIVE_TEXT
        )
        self.accents[item["id"]].configure(fg_color=PRIMARY)

        if self.on_select:
            self.on_select(item["id"])

    def set_active(self, item_id: str):
        """Programmatically set active item."""
        if item_id in self.buttons:
            if self.active_item:
                self.buttons[self.active_item].configure(
                    fg_color="transparent",
                    text_color=TEXT_SECONDARY
                )
                self.accents[self.active_item].configure(fg_color="transparent")
            self.active_item = item_id
            self.buttons[item_id].configure(
                fg_color=SIDEBAR_ACTIVE,
                text_color=SIDEBAR_ACTIVE_TEXT
            )
            self.accents[item_id].configure(fg_color=PRIMARY)
