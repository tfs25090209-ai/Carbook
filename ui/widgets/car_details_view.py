from __future__ import annotations

from typing import Any, Dict, Optional

import customtkinter as ctk

from theme.colors import (
    ACCENT_ERROR,
    ACCENT_SUCCESS,
    ACCENT_WARNING,
    BG_CARD,
    BG_DARK,
    BG_LIGHT,
    BG_MEDIUM,
    BORDER,
    BORDER_LIGHT,
    CARD_RADIUS,
    PRIMARY,
    PRIMARY_HOVER,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    PAGE_PAD_X,
)
from utils.image_loader import get_cached_image
from utils.ui_helpers import StatusChip


class CarDetailsView(ctk.CTkFrame):
    """
    Reusable premium car details component.

    Renders (for a single car dict):
    - car name
    - price per day
    - status
    - transmission
    - fuel type
    - seats
    - description
    - large premium layout
    - placeholder area for car image
    """

    def __init__(
        self,
        master,
        car: Optional[Dict[str, Any]] = None,
        on_book_now: Optional[Any] = None,
        **kwargs,
    ):
        kwargs.setdefault("fg_color", BG_MEDIUM)
        kwargs.setdefault("corner_radius", 0)
        super().__init__(master, **kwargs)

        self.car: Dict[str, Any] = car or {}
        self.image_refs = []
        self.on_book_now = on_book_now

        self._build_ui()
        self.set_car(self.car)

    def _build_ui(self):
        # Outer premium container
        self.container = ctk.CTkFrame(
            self,
            fg_color=BG_DARK,
            corner_radius=CARD_RADIUS,
            border_color=BORDER,
            border_width=1,
        )
        self.container.grid(row=0, column=0, sticky="nsew", padx=PAGE_PAD_X, pady=PAGE_PAD_X)
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_columnconfigure(1, weight=1)

        # Left: image placeholder (large)
        self.left = ctk.CTkFrame(
            self.container,
            fg_color="transparent",
        )
        self.left.grid(row=0, column=0, sticky="nsew", padx=(PAGE_PAD_X, 12), pady=PAGE_PAD_X)
        self.left.grid_columnconfigure(0, weight=1)
        self.left.grid_rowconfigure(0, weight=1)

        self.image_placeholder = ctk.CTkFrame(
            self.left,
            fg_color=BG_LIGHT,
            corner_radius=CARD_RADIUS,
            border_color=BORDER_LIGHT,
            border_width=1,
        )
        self.image_placeholder.grid(row=0, column=0, sticky="nsew")
        self.image_placeholder.grid_columnconfigure(0, weight=1)
        self.image_placeholder.grid_rowconfigure(0, weight=1)

        # Placeholder artwork + hint
        self.image_icon = ctk.CTkLabel(
            self.image_placeholder,
            text="◆",
            font=ctk.CTkFont(size=44, weight="bold"),
            text_color=BORDER_LIGHT,
        )
        self.image_icon.grid(row=0, column=0, sticky="n", pady=(26, 6))

        self.image_hint = ctk.CTkLabel(
            self.image_placeholder,
            text="Car image placeholder",
            font=ctk.CTkFont(size=13, family="Helvetica"),
            text_color=TEXT_MUTED,
        )
        self.image_hint.grid(row=1, column=0, sticky="n", pady=(0, 18))

        # Right: textual details
        self.right = ctk.CTkFrame(
            self.container,
            fg_color="transparent",
        )
        self.right.grid(row=0, column=1, sticky="nsew", padx=(12, PAGE_PAD_X), pady=PAGE_PAD_X)
        self.right.grid_columnconfigure(0, weight=1)

        # Title row
        self.name_label = ctk.CTkLabel(
            self.right,
            text="Car Name",
            font=ctk.CTkFont(size=24, weight="bold", family="Helvetica"),
            text_color=TEXT_PRIMARY,
        )
        self.name_label.grid(row=0, column=0, sticky="w")

        # Price row
        self.price_label = ctk.CTkLabel(
            self.right,
            text="₹0/day",
            font=ctk.CTkFont(size=14, weight="bold", family="Helvetica"),
            text_color=PRIMARY,
        )
        self.price_label.grid(row=1, column=0, sticky="w", pady=(10, 16))

        # Status chip
        self.status_chip = StatusChip(self.right, text="Status", status_type="car")
        self.status_chip.grid(row=2, column=0, sticky="w", pady=(0, 18))

        # Details grid (transmission/fuel/seats/category)
        self.meta_grid = ctk.CTkFrame(self.right, fg_color="transparent")
        self.meta_grid.grid(row=3, column=0, sticky="ew", pady=(0, 16))
        self.meta_grid.grid_columnconfigure((0, 1), weight=1)

        self.transmission_title = self._meta_title(self.meta_grid, "Transmission")
        self.transmission_value = self._meta_value(self.meta_grid, "")

        self.fuel_title = self._meta_title(self.meta_grid, "Fuel Type")
        self.fuel_value = self._meta_value(self.meta_grid, "")

        self.seats_title = self._meta_title(self.meta_grid, "Seats")
        self.seats_value = self._meta_value(self.meta_grid, "")

        self.category_title = self._meta_title(self.meta_grid, "Category")
        self.category_value = self._meta_value(self.meta_grid, "")

        self._layout_meta()

        # Description
        self.desc_title = ctk.CTkLabel(
            self.right,
            text="Description",
            font=ctk.CTkFont(size=13, weight="bold", family="Helvetica"),
            text_color=TEXT_SECONDARY,
        )
        self.desc_title.grid(row=5, column=0, sticky="w", pady=(0, 8))

        self.desc_label = ctk.CTkLabel(
            self.right,
            text="",
            font=ctk.CTkFont(size=13, family="Helvetica"),
            text_color=TEXT_MUTED,
            wraplength=520,
            justify="left",
        )
        self.desc_label.grid(row=6, column=0, sticky="w")

        # Premium actions area (UI-only; no booking logic wired)
        self.actions = ctk.CTkFrame(
            self.right,
            fg_color="transparent",
        )
        self.actions.grid(row=7, column=0, sticky="ew", pady=(22, 0))
        self.actions.grid_columnconfigure(0, weight=1)

        self.book_now_button = ctk.CTkButton(
            self.actions,
            text="Book Now",
            corner_radius=10,
            height=44,
            font=ctk.CTkFont(size=16, weight="bold", family="Helvetica"),
            fg_color=PRIMARY,
            hover_color=PRIMARY_HOVER,
            text_color=TEXT_PRIMARY,
            command=self._handle_book_now,
        )
        self.book_now_button.grid(row=0, column=0, sticky="ew", padx=0, pady=0)

    def _layout_meta(self):
        # 2x2 grid: (transmission, fuel) on row0, (seats, category) on row1
        self.transmission_title.grid(row=0, column=0, sticky="w")
        self.transmission_value.grid(row=1, column=0, sticky="w", pady=(6, 0))

        self.fuel_title.grid(row=0, column=1, sticky="w")
        self.fuel_value.grid(row=1, column=1, sticky="w", pady=(6, 0))

        self.seats_title.grid(row=2, column=0, sticky="w", pady=(12, 0))
        self.seats_value.grid(row=3, column=0, sticky="w", pady=(6, 0))

        self.category_title.grid(row=2, column=1, sticky="w", pady=(12, 0))
        self.category_value.grid(row=3, column=1, sticky="w", pady=(6, 0))

        self.meta_grid.grid_rowconfigure(0, weight=0)
        self.meta_grid.grid_rowconfigure(1, weight=0)
        self.meta_grid.grid_rowconfigure(2, weight=0)
        self.meta_grid.grid_rowconfigure(3, weight=0)

    @staticmethod
    def _meta_title(parent, text: str):
        label = ctk.CTkLabel(
            parent,
            text=text,
            font=ctk.CTkFont(size=12, weight="bold", family="Helvetica"),
            text_color=TEXT_SECONDARY,
        )
        return label

    @staticmethod
    def _meta_value(parent, text: str):
        label = ctk.CTkLabel(
            parent,
            text=text,
            font=ctk.CTkFont(size=14, family="Helvetica"),
            text_color=TEXT_PRIMARY,
        )
        return label

    def set_car(self, car: Dict[str, Any]):
        """Update UI from the provided car dict."""
        self.car = car or {}

        brand = str(self.car.get("brand") or "")
        model = str(self.car.get("model") or "")
        name = f"{brand} {model}".strip() or "Car Name"
        self.name_label.configure(text=name)

        daily_rate = self.car.get("daily_rate", 0) or 0
        try:
            daily_rate_fmt = f"₹{float(daily_rate):,.0f}/day"
        except (TypeError, ValueError):
            daily_rate_fmt = f"₹{daily_rate}/day"
        self.price_label.configure(text=daily_rate_fmt)

        status = str(self.car.get("status") or "available").strip().lower()
        self._render_status(status)

        transmission = str(self.car.get("transmission") or "—").strip().title()
        fuel_type = str(self.car.get("fuel_type") or "—").strip().title()
        seats = self.car.get("seats", "—")
        seats_str = str(seats).strip() if seats is not None else "—"

        category = str(self.car.get("category") or "—").strip().title()
        self.transmission_value.configure(text=transmission)
        self.fuel_value.configure(text=fuel_type)
        self.seats_value.configure(text=f"{seats_str} seats" if seats_str != "—" else "—")
        self.category_value.configure(text=category)

        description = self.car.get("description") or ""
        description = str(description).strip()
        self.desc_label.configure(text=description if description else "No description provided.")

        self._render_image(self.car.get("image_url"))

    def _render_status(self, status: str):
        self.status_chip.set_text(status, status_type="car")

    def _handle_book_now(self):
        """
        Wire the "Book Now" button to the page-level booking flow.
        Expects `on_book_now` callback to be provided by the hosting page.
        """
        if not self.on_book_now or not self.car:
            return

        try:
            # Preferred: callback(car)
            self.on_book_now(self.car)
        except TypeError:
            # Fallback: callback() if implemented differently
            self.on_book_now()

    def _render_image(self, image_url: Optional[str]):
        for child in self.image_placeholder.winfo_children():
            child.destroy()

        self.image_refs.clear()

        ctk_image = get_cached_image(image_url, 640, 420)
        if ctk_image is not None:
            self.image_refs.append(ctk_image)
            label = ctk.CTkLabel(self.image_placeholder, text="", image=ctk_image)
            label.grid(row=0, column=0, sticky="nsew")
            return

        self.image_icon = ctk.CTkLabel(
            self.image_placeholder,
            text="◆",
            font=ctk.CTkFont(size=44, weight="bold"),
            text_color=BORDER_LIGHT,
        )
        self.image_icon.grid(row=0, column=0, sticky="n", pady=(26, 6))

        self.image_hint = ctk.CTkLabel(
            self.image_placeholder,
            text="Car image placeholder",
            font=ctk.CTkFont(size=13, family="Helvetica"),
            text_color=TEXT_MUTED,
        )
        self.image_hint.grid(row=1, column=0, sticky="n", pady=(0, 18))
