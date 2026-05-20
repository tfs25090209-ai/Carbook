"""My Bookings page — Luxury Edition."""

from datetime import datetime
from typing import Dict

import customtkinter as ctk

from services.booking_service import BookingService
from ui.pages.base_page import BasePage
from theme.colors import *
from utils.auth import Session
from utils.ui_helpers import EmptyState, StatusChip, apply_card_hover


class MyBookingsPage(BasePage):
    """User bookings history and active bookings."""

    def __init__(self, master, app, **kwargs):
        super().__init__(master, app, **kwargs)
        self.bookings = []
        self.active_filter = "all"
        self._setup_ui()
        self.refresh()

    def _setup_ui(self):
        """Build the page layout."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)   # header
        self.grid_rowconfigure(1, weight=0)   # filter tabs
        self.grid_rowconfigure(2, weight=1)   # bookings list (expands)
        self.grid_rowconfigure(3, weight=0)   # error label (fixed)

        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=PAGE_PAD_X, pady=(PAGE_PAD_Y, 14))
        header.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            header,
            text="My Bookings",
            font=ctk.CTkFont(size=28, weight="bold", family="Helvetica"),
            text_color=TEXT_PRIMARY
        )
        title.grid(row=0, column=0, sticky="w")

        # Subtitle with booking count
        self.subtitle = ctk.CTkLabel(
            header,
            text="",
            font=ctk.CTkFont(size=13, family="Helvetica"),
            text_color=TEXT_SECONDARY
        )
        self.subtitle.grid(row=1, column=0, sticky="w", pady=(4, 0))

        # Filter tabs — luxury styling
        filter_frame = ctk.CTkFrame(
            self,
            fg_color=BG_CARD,
            corner_radius=CARD_RADIUS,
            border_color=BORDER,
            border_width=1
        )
        filter_frame.grid(row=1, column=0, sticky="ew", padx=PAGE_PAD_X, pady=(0, 18))
        filter_frame.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="filters")

        filters = [
            ("all", "All"),
            ("pending", "Pending"),
            ("confirmed", "Confirmed"),
            ("completed", "Completed"),
        ]

        for col, (filter_id, label) in enumerate(filters):
            btn = ctk.CTkButton(
                filter_frame,
                text=label,
                height=40,
                fg_color=PRIMARY if filter_id == "all" else "transparent",
                text_color=BG_DARK if filter_id == "all" else TEXT_SECONDARY,
                hover_color=BG_CARD_HOVER,
                font=ctk.CTkFont(size=12, weight="bold" if filter_id == "all" else "normal", family="Helvetica"),
                corner_radius=6,
                command=lambda f=filter_id: self._set_filter(f)
            )
            btn.grid(row=0, column=col, sticky="ew", padx=8, pady=10)
            setattr(self, f"filter_{filter_id}", btn)

        # Bookings container
        self.bookings_container = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=BG_LIGHT,
            scrollbar_button_hover_color=BORDER
        )
        self.bookings_container.grid(row=2, column=0, sticky="nsew", padx=PAGE_PAD_X, pady=(0, 20))
        self.bookings_container.grid_columnconfigure(0, weight=1)

    def refresh(self):
        """Reload bookings."""
        user_id = Session.get_user_id()
        self.bookings = BookingService.get_user_bookings(user_id) if user_id is not None else []
        self._render_bookings()

    def _set_filter(self, filter_id: str):
        """Switch active filter — luxury active state."""
        self.active_filter = filter_id

        # Update button states
        for fid, _ in [("all", ""), ("pending", ""), ("confirmed", ""), ("completed", "")]:
            btn = getattr(self, f"filter_{fid}")
            is_active = fid == filter_id
            btn.configure(
                fg_color=PRIMARY if is_active else "transparent",
                text_color=BG_DARK if is_active else TEXT_SECONDARY,
                font=ctk.CTkFont(size=12, weight="bold" if is_active else "normal", family="Helvetica")
            )

        self._render_bookings()

    def _render_bookings(self):
        """Render booking cards."""
        for widget in self.bookings_container.winfo_children():
            widget.destroy()

        # Filter bookings
        filtered = self.bookings if self.active_filter == "all" else \
            [b for b in self.bookings if b["status"] == self.active_filter]

        count = len(filtered)
        total = len(self.bookings)
        self.subtitle.configure(
            text=f"{count} of {total} booking{'s' if total != 1 else ''}"
        )

        if not filtered:
            self._render_empty_state()
            return

        for index, booking in enumerate(filtered):
            self._create_booking_card(booking, index)

    def _render_empty_state(self):
        """Show empty state when no bookings."""
        subtitle = "No bookings match this filter." if self.active_filter != "all" else "Start your journey with our premium collection"
        empty = EmptyState(
            self.bookings_container,
            icon="◇",
            title="No bookings yet" if self.active_filter == "all" else "No matching bookings",
            subtitle=subtitle,
        )
        empty.grid(row=0, column=0, sticky="nsew", pady=20)

    def _create_booking_card(self, booking: Dict, index: int):
        """Create a booking card — luxury styling."""
        card = ctk.CTkFrame(
            self.bookings_container,
            fg_color=BG_CARD,
            corner_radius=CARD_RADIUS,
            border_color=BORDER,
            border_width=1
        )
        card.grid(row=index, column=0, sticky="ew", pady=8)
        card.grid_columnconfigure(0, weight=1)
        card.grid_columnconfigure(1, weight=0)

        # Left content
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.grid(row=0, column=0, sticky="nsew", padx=20, pady=18)
        content.grid_columnconfigure(0, weight=1)

        # Car name
        car_name = ctk.CTkLabel(
            content,
            text=f"{booking['brand']} {booking['model']}",
            font=ctk.CTkFont(size=18, weight="bold", family="Helvetica"),
            text_color=TEXT_PRIMARY
        )
        car_name.grid(row=0, column=0, sticky="w")

        # Booking details
        start = self._format_date(booking["pickup_date"])
        end = self._format_date(booking["dropoff_date"])
        days = (booking["dropoff_date"] - booking["pickup_date"]).days

        details = ctk.CTkLabel(
            content,
            text=f"{start} → {end} · {days} day{'s' if days != 1 else ''}",
            font=ctk.CTkFont(size=13, family="Helvetica"),
            text_color=TEXT_SECONDARY
        )
        details.grid(row=1, column=0, sticky="w", pady=(6, 0))

        # Price
        price = ctk.CTkLabel(
            content,
            text=f"₹{booking['total_price']:,.0f}",
            font=ctk.CTkFont(size=15, weight="bold", family="Helvetica"),
            text_color=PRIMARY
        )
        price.grid(row=2, column=0, sticky="w", pady=(8, 0))

        # Right side — premium status chip
        display_text = self._display_status(booking["status"])
        status_chip = StatusChip(card, text=display_text, status_type="booking")
        status_chip.grid(row=0, column=1, sticky="e", padx=20, pady=18)

        # Action buttons based on status
        if booking["status"] in ("pending", "confirmed"):
            actions = ctk.CTkFrame(content, fg_color="transparent")
            actions.grid(row=3, column=0, sticky="w", pady=(12, 0))
            actions.grid_columnconfigure((0, 1), weight=0)

            cancel_btn = ctk.CTkButton(
                actions,
                text="Cancel",
                width=80,
                height=30,
                fg_color="transparent",
                hover_color=ACCENT_ERROR,
                text_color=ACCENT_ERROR,
                font=ctk.CTkFont(size=11, family="Helvetica"),
                corner_radius=6,
                border_color=ACCENT_ERROR,
                border_width=1,
                command=lambda: self._cancel_booking(booking)
            )
            cancel_btn.grid(row=0, column=0, padx=(0, 10))

            if booking["status"] == "confirmed":
                extend_btn = ctk.CTkButton(
                    actions,
                    text="Extend",
                    width=80,
                    height=30,
                    fg_color=BG_LIGHT,
                    hover_color=BORDER,
                    text_color=TEXT_PRIMARY,
                    font=ctk.CTkFont(size=11, family="Helvetica"),
                    corner_radius=6,
                    command=lambda: self._extend_booking(booking)
                )
                extend_btn.grid(row=0, column=1)

        apply_card_hover(card)

    def _format_date(self, date_value: str) -> str:
        if isinstance(date_value, datetime):
            dt = date_value
        else:
            dt = datetime.strptime(str(date_value), "%Y-%m-%d")

        return dt.strftime("%b %d, %Y")

    def _display_status(self, status: str) -> str:
        """Return the user-facing status label (premium display set)."""
        display = {
            "pending": "Rented",
            "confirmed": "Rented",
            "active": "Rented",
            "completed": "Completed",
            "cancelled": "Cancelled",
        }
        return display.get(status, status.title())

    def _cancel_booking(self, booking: Dict):
        """Cancel a booking."""
        dialog = ctk.CTkInputDialog(
            text="Are you sure you want to cancel this booking?\n\nType 'cancel' to confirm:",
            title="Cancel Booking"
        )
        response = dialog.get_input()
        if response and response.lower() == "cancel":
            success, msg = BookingService.cancel(booking["id"])
            if success:
                self.refresh()
            else:
                self._show_error(msg)

    def _extend_booking(self, booking: Dict):
        """Extend a booking."""
        # Simple extension dialog
        dialog = ctk.CTkInputDialog(
            text="Enter new end date (YYYY-MM-DD):",
            title="Extend Booking"
        )
        new_end = dialog.get_input()
        if new_end:
            success, msg = BookingService.extend(booking["id"], new_end)
            if success:
                self.refresh()
            else:
                self._show_error(msg)

    def _show_error(self, message: str):
        """Show error notification."""
        error = ctk.CTkLabel(
            self,
            text=message,
            font=ctk.CTkFont(size=12, family="Helvetica"),
            text_color=ACCENT_ERROR
        )
        error.grid(row=3, column=0, sticky="w", padx=PAGE_PAD_X, pady=(0, 10))
        self.after(3000, error.destroy)