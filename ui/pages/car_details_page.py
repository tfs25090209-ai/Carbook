from __future__ import annotations

from typing import Any, Dict, Optional

import customtkinter as ctk

from services.booking_service import BookingService
from theme.colors import ACCENT_SUCCESS

from utils.auth import Session
from ui.pages.base_page import BasePage
from ui.forms.booking_form import BookingForm
from ui.dialogs.booking_confirmation_dialog import BookingConfirmationDialog
from ui.widgets.car_details_view import CarDetailsView


class CarDetailsPage(BasePage):
    """
    Page wrapper for the reusable CarDetailsView.
    """

    def __init__(
        self,
        master,
        app,
        car: Optional[Dict[str, Any]] = None,
        **kwargs,
    ):
        super().__init__(master, app, **kwargs)

        self.car: Optional[Dict[str, Any]] = car
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.details = CarDetailsView(
            self,
            car=self.car,
            on_book_now=lambda car: self._open_booking_dialog(car),
        )
        self.details.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)

    def set_car(self, car: Dict[str, Any]):
        """Update page content from a car dict (refreshes the view)."""
        self.car = car
        self.refresh()

    def _open_booking_dialog(self, car: Dict[str, Any]):
        """Open the booking form for a selected car — luxury styling (reused)."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Book Car")
        dialog.geometry("460x540")
        dialog.resizable(False, False)
        dialog.configure(fg_color=self.cget("fg_color") or "#151515")
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()

        form = BookingForm(dialog, car)
        form.pack(fill="both", expand=True)

        # BookingForm attributes are used as callbacks inside the widget.
        # Keep assignments local and quiet type-checker warnings.
        form.on_cancel = dialog.destroy  # type: ignore[assignment]
        form.on_confirm = lambda values: self._create_booking(dialog, form, car, values)  # type: ignore[assignment]

    def _create_booking(self, dialog, form, car: Dict[str, Any], values: Dict[str, Any]):
        user_id = Session.get_user_id()
        if user_id is None:
            form.set_error("Please login to book a car.")
            return

        success, message, booking = BookingService.create_booking(
            user_id=user_id,
            car_id=car["id"],
            start_date_text=values["start_date"],
            end_date_text=values["end_date"],
            pickup_location=values["pickup_location"],
            dropoff_location=values["dropoff_location"],
        )

        if not success:
            form.set_error(message)
            return

        dialog.destroy()
        # Preserve current booking confirmation styling/behavior
        self._set_message(message, ACCENT_SUCCESS)
        # booking is produced by BookingService.create_booking on success
        BookingConfirmationDialog(self, booking)  # type: ignore[arg-type]

    def _set_message(self, message: str, color: str):
        # BasePage exposes a message label in this codebase; keep it consistent with other pages.
        if hasattr(self, "message_label") and self.message_label is not None:
            self.message_label.configure(text=message, text_color=color)
            return
        # fallback (safe no-op if message_label not present)
        try:
            self.message_label = ctk.CTkLabel(self, text=message, text_color=color)
            self.message_label.grid(row=99, column=0, sticky="w")
        except Exception:
            pass

    def refresh(self):
        """Render latest car info."""
        if not self.car:
            # Provide an empty dict so labels render placeholders
            self.details.set_car({})
        else:
            self.details.set_car(self.car)
