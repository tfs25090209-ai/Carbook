"""Booking form for car reservations — luxury styling."""

import tkinter as tk
from typing import Dict

import customtkinter as ctk

from services.booking_service import BookingService
from theme.colors import (
    ACCENT_ERROR,
    BG_CARD,
    BG_DARK,
    BG_LIGHT,
    BORDER,
    BORDER_LIGHT,
    CARD_RADIUS,
    PRIMARY,
    PRIMARY_HOVER,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)


class BookingForm(ctk.CTkFrame):
    """Form for booking a selected car — luxury styling."""

    def __init__(self, master, car: Dict):
        super().__init__(master, fg_color=BG_DARK)
        self.car = car
        self.on_confirm = None
        self.on_cancel = None
        self.start_var = tk.StringVar()
        self.end_var = tk.StringVar()
        self.pickup_var = tk.StringVar(value="Main Branch")
        self.dropoff_var = tk.StringVar(value="Main Branch")
        self.total_label = None
        self.error_label = None
        self.confirm_btn = None
        self._setup_ui()

    def _setup_ui(self):
        self.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            self,
            text=f"Book {self.car['brand']} {self.car['model']}",
            font=ctk.CTkFont(size=22, weight="bold", family="Helvetica"),
            text_color=TEXT_PRIMARY
        )
        title.grid(row=0, column=0, sticky="w", padx=24, pady=(24, 6))

        subtitle = ctk.CTkLabel(
            self,
            text=f"₹{self.car['daily_rate']:,.0f}/day · {self.car['license_plate']}",
            font=ctk.CTkFont(size=13, family="Helvetica"),
            text_color=PRIMARY
        )
        subtitle.grid(row=1, column=0, sticky="w", padx=24, pady=(0, 18))

        self._add_entry(2, "Start Date", self.start_var, "YYYY-MM-DD")
        self._add_entry(3, "End Date", self.end_var, "YYYY-MM-DD")
        self._add_entry(4, "Pickup Location", self.pickup_var, "Main Branch")
        self._add_entry(5, "Dropoff Location", self.dropoff_var, "Main Branch")

        self.start_var.trace_add("write", lambda *_args: self._refresh_total())
        self.end_var.trace_add("write", lambda *_args: self._refresh_total())

        # Summary card
        self.summary_card = ctk.CTkFrame(
            self,
            fg_color=BG_CARD,
            corner_radius=CARD_RADIUS,
            border_color=BORDER,
            border_width=1,
        )
        self.summary_card.grid(row=6, column=0, sticky="ew", padx=24, pady=(14, 8))
        self.summary_card.grid_columnconfigure(1, weight=1)

        # Daily rate row
        ctk.CTkLabel(
            self.summary_card,
            text="Daily Rate",
            font=ctk.CTkFont(size=12, family="Helvetica"),
            text_color=TEXT_SECONDARY,
        ).grid(row=0, column=0, sticky="w", padx=16, pady=(14, 6))

        self.rate_value = ctk.CTkLabel(
            self.summary_card,
            text=f"₹{self.car['daily_rate']:,.0f}",
            font=ctk.CTkFont(size=12, family="Helvetica"),
            text_color=TEXT_PRIMARY,
        )
        self.rate_value.grid(row=0, column=1, sticky="e", padx=16, pady=(14, 6))

        # Days row
        ctk.CTkLabel(
            self.summary_card,
            text="Duration",
            font=ctk.CTkFont(size=12, family="Helvetica"),
            text_color=TEXT_SECONDARY,
        ).grid(row=1, column=0, sticky="w", padx=16, pady=2)

        self.days_value = ctk.CTkLabel(
            self.summary_card,
            text="—",
            font=ctk.CTkFont(size=12, family="Helvetica"),
            text_color=TEXT_PRIMARY,
        )
        self.days_value.grid(row=1, column=1, sticky="e", padx=16, pady=2)

        # Divider
        ctk.CTkFrame(
            self.summary_card,
            fg_color=BORDER,
            height=1,
        ).grid(row=2, column=0, columnspan=2, sticky="ew", padx=16, pady=8)

        # Total row
        ctk.CTkLabel(
            self.summary_card,
            text="Total",
            font=ctk.CTkFont(size=14, weight="bold", family="Helvetica"),
            text_color=TEXT_PRIMARY,
        ).grid(row=3, column=0, sticky="w", padx=16, pady=(6, 14))

        self.total_value = ctk.CTkLabel(
            self.summary_card,
            text="₹0",
            font=ctk.CTkFont(size=14, weight="bold", family="Helvetica"),
            text_color=PRIMARY,
        )
        self.total_value.grid(row=3, column=1, sticky="e", padx=16, pady=(6, 14))

        self.error_label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=12, family="Helvetica"),
            text_color=ACCENT_ERROR
        )
        self.error_label.grid(row=7, column=0, sticky="w", padx=24, pady=(0, 12))

        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.grid(row=8, column=0, sticky="ew", padx=24, pady=(8, 24))
        actions.grid_columnconfigure((0, 1), weight=1)

        cancel = ctk.CTkButton(
            actions,
            text="Cancel",
            height=38,
            fg_color=BG_LIGHT,
            hover_color=BORDER,
            text_color=TEXT_PRIMARY,
            font=ctk.CTkFont(size=12, family="Helvetica"),
            corner_radius=CARD_RADIUS,
            command=lambda: self.on_cancel and self.on_cancel()
        )
        cancel.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        self.confirm_btn = ctk.CTkButton(
            actions,
            text="Confirm Booking",
            height=38,
            fg_color=PRIMARY,
            hover_color=PRIMARY_HOVER,
            text_color=BG_DARK,
            font=ctk.CTkFont(size=12, weight="bold", family="Helvetica"),
            corner_radius=CARD_RADIUS,
            command=self._confirm
        )
        self.confirm_btn.grid(row=0, column=1, sticky="ew", padx=(8, 0))

    def _add_entry(self, row: int, label: str, variable: tk.StringVar, placeholder: str):
        wrapper = ctk.CTkFrame(self, fg_color="transparent")
        wrapper.grid(row=row, column=0, sticky="ew", padx=24, pady=6)
        wrapper.grid_columnconfigure(0, weight=1)

        field_label = ctk.CTkLabel(
            wrapper,
            text=label,
            font=ctk.CTkFont(size=12, family="Helvetica"),
            text_color=TEXT_SECONDARY
        )
        field_label.grid(row=0, column=0, sticky="w")

        entry = ctk.CTkEntry(
            wrapper,
            textvariable=variable,
            height=38,
            fg_color=BG_LIGHT,
            border_color=BORDER,
            text_color=TEXT_PRIMARY,
            font=ctk.CTkFont(size=12, family="Helvetica"),
            placeholder_text=placeholder,
            placeholder_text_color=TEXT_MUTED
        )
        entry.grid(row=1, column=0, sticky="ew", pady=(4, 0))

    def _refresh_total(self):
        success, message, quote = BookingService.calculate_total(
            self.car["id"],
            self.start_var.get(),
            self.end_var.get()
        )
        if success:
            daily = float(self.car["daily_rate"])
            self.rate_value.configure(text=f"₹{daily:,.0f}")
            self.days_value.configure(text=f"{quote['total_days']} day(s)")
            self.total_value.configure(text=f"₹{quote['total_price']:,.0f}")
            self.error_label.configure(text="")
        elif self.start_var.get() or self.end_var.get():
            self.days_value.configure(text="—")
            self.total_value.configure(text="₹0")
            self.error_label.configure(text=message)
        else:
            self.days_value.configure(text="—")
            self.total_value.configure(text="₹0")
            self.error_label.configure(text="")

    def _confirm(self):
        if self.on_confirm:
            self.confirm_btn.configure(text="Processing...", state="disabled")
            self.update_idletasks()
            self.on_confirm({
                "start_date": self.start_var.get(),
                "end_date": self.end_var.get(),
                "pickup_location": self.pickup_var.get(),
                "dropoff_location": self.dropoff_var.get(),
            })

    def set_error(self, message: str):
        self.error_label.configure(text=message)
        self.confirm_btn.configure(text="Confirm Booking", state="normal")
