"""Reusable premium UI components — StatusChip, EmptyState, hover effects."""

from typing import Optional
import customtkinter as ctk

from theme.colors import (
    BG_CARD,
    BG_LIGHT,
    BORDER,
    BORDER_LIGHT,
    CARD_RADIUS,
    PRIMARY_LIGHT,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)
from theme.status_styles import car_status_style, booking_status_style


class StatusChip(ctk.CTkFrame):
    """Consistent premium status chip used across all pages."""

    _PAD_X = 14
    _PAD_Y = 5

    def __init__(self, master, text: str, status_type: str = "car", **kwargs):
        status_key = text.strip().lower().replace(" ", "_").replace("-", "_")
        if status_type == "booking":
            text_color, bg_color = booking_status_style(status_key)
        else:
            text_color, bg_color = car_status_style(status_key)

        kwargs.setdefault("fg_color", bg_color)
        kwargs.setdefault("corner_radius", 999)
        kwargs.setdefault("border_color", BORDER_LIGHT)
        kwargs.setdefault("border_width", 1)
        super().__init__(master, **kwargs)

        self._text_color = text_color
        self._label = ctk.CTkLabel(
            self,
            text=status_key.replace("_", " ").title(),
            font=ctk.CTkFont(size=11, weight="bold", family="Helvetica"),
            text_color=text_color,
        )
        self._label.pack(padx=self._PAD_X, pady=self._PAD_Y)

    def set_text(self, text: str, status_type: str = "car"):
        status_key = text.strip().lower().replace(" ", "_").replace("-", "_")
        if status_type == "booking":
            text_color, bg_color = booking_status_style(status_key)
        else:
            text_color, bg_color = car_status_style(status_key)
        self._label.configure(text=status_key.replace("_", " ").title(), text_color=text_color)
        self.configure(fg_color=bg_color)


class EmptyState(ctk.CTkFrame):
    """Premium empty state for pages with no data."""

    def __init__(
        self,
        master,
        icon: str = "◇",
        title: str = "No data",
        subtitle: str = "",
        **kwargs,
    ):
        kwargs.setdefault("fg_color", BG_CARD)
        kwargs.setdefault("corner_radius", CARD_RADIUS)
        kwargs.setdefault("border_color", BORDER)
        kwargs.setdefault("border_width", 1)
        super().__init__(master, **kwargs)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=0)
        self.grid_rowconfigure(3, weight=1)

        icon_label = ctk.CTkLabel(
            self,
            text=icon,
            font=ctk.CTkFont(size=40),
            text_color=BORDER_LIGHT,
        )
        icon_label.grid(row=1, column=0, pady=(40, 12))

        title_label = ctk.CTkLabel(
            self,
            text=title,
            font=ctk.CTkFont(size=18, weight="bold", family="Helvetica"),
            text_color=TEXT_PRIMARY,
        )
        title_label.grid(row=2, column=0)

        if subtitle:
            subtitle_label = ctk.CTkLabel(
                self,
                text=subtitle,
                font=ctk.CTkFont(size=13, family="Helvetica"),
                text_color=TEXT_SECONDARY,
            )
            subtitle_label.grid(row=3, column=0, pady=(6, 40))


def apply_card_hover(card_frame: ctk.CTkFrame, hover_color: str = PRIMARY_LIGHT):
    """Bind subtle border color change on mouse hover."""
    def _on_enter(_event):
        card_frame._orig_border = card_frame.cget("border_color")
        card_frame.configure(border_color=hover_color)
    def _on_leave(_event):
        orig = getattr(card_frame, "_orig_border", BORDER)
        card_frame.configure(border_color=orig)
    card_frame.bind("<Enter>", _on_enter)
    card_frame.bind("<Leave>", _on_leave)
