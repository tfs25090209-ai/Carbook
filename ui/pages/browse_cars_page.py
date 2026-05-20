"""Browse and manage cars page — Luxury Edition."""

import tkinter as tk
from typing import Dict, Optional

import customtkinter as ctk

from services.car_service import CarService
from services.booking_service import BookingService
from ui.pages.base_page import BasePage
from ui.forms.car_form import CarForm
from ui.forms.booking_form import BookingForm
from ui.dialogs.confirm_action_dialog import ConfirmActionDialog
from ui.dialogs.booking_confirmation_dialog import BookingConfirmationDialog
from theme.colors import *
from theme.typography import font_heading_lg, font_label
from utils.auth import Session
from utils.image_loader import get_cached_image
from utils.ui_helpers import EmptyState, StatusChip, apply_card_hover


class BrowseCarsPage(BasePage):
    """Car inventory management page."""

    def __init__(self, master, app, is_admin=False, **kwargs):
        super().__init__(master, app, **kwargs)
        self.cars = []
        self.image_refs = []
        self._search_timer = None
        self.search_var = tk.StringVar()
        self.category_var = tk.StringVar(value="all")
        self.status_var = tk.StringVar(value="all")
        self.message_label = None
        self.is_admin = is_admin
        self._setup_ui()

    # ══════════════════════════════════════════════════════════════
    # UI Setup
    # ══════════════════════════════════════════════════════════════

    def _setup_ui(self):
        """Build the page layout."""
        # Row 0: header (fixed), Row 1: controls (fixed),
        # Row 2: cars scrollable (expands), Row 3: status label (fixed)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=0)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=PAGE_PAD_X, pady=(PAGE_PAD_Y, 12))
        header.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            header,
            text="Manage Cars" if self.is_admin else "Browse Cars",
            font=font_heading_lg(bold=True),
            text_color=TEXT_PRIMARY
        )
        title.grid(row=0, column=0, sticky="w")

        # Add button — only for admins
        if self.is_admin:
            add_button = ctk.CTkButton(
                header,
                text="+ Add Car",
                width=120,
                height=38,
                fg_color=PRIMARY,
                hover_color=PRIMARY_HOVER,
                text_color=BG_DARK,
                font=ctk.CTkFont(size=12, weight="bold", family="Helvetica"),
                corner_radius=CARD_RADIUS,
                command=self._open_add_dialog
            )
            add_button.grid(row=0, column=1, sticky="e")

        # Controls bar
        controls = ctk.CTkFrame(
            self,
            fg_color=BG_CARD,
            corner_radius=CARD_RADIUS,
            border_color=BORDER,
            border_width=1
        )
        controls.grid(row=1, column=0, sticky="ew", padx=PAGE_PAD_X, pady=(0, 12))
        controls.grid_columnconfigure(0, weight=1)

        search_entry = ctk.CTkEntry(
            controls,
            textvariable=self.search_var,
            height=38,
            fg_color=BG_LIGHT,
            border_color=BORDER,
            placeholder_text="Search by brand, model, plate, or color",
            font=ctk.CTkFont(size=12, family="Helvetica"),
            text_color=TEXT_PRIMARY,
            placeholder_text_color=TEXT_MUTED
        )
        search_entry.grid(row=0, column=0, sticky="ew", padx=(16, 10), pady=14)
        search_entry.bind("<KeyRelease>", lambda _event: self._on_search_change())

        category_menu = ctk.CTkOptionMenu(
            controls,
            values=list(CarService.CATEGORIES),
            variable=self.category_var,
            width=130,
            fg_color=BG_LIGHT,
            button_color=PRIMARY,
            button_hover_color=PRIMARY_HOVER,
            font=ctk.CTkFont(size=12, family="Helvetica"),
            text_color=TEXT_PRIMARY,
            command=lambda _value: self.refresh_cars()
        )
        category_menu.grid(row=0, column=1, padx=10, pady=14)

        status_menu = ctk.CTkOptionMenu(
            controls,
            values=list(CarService.STATUSES),
            variable=self.status_var,
            width=140,
            fg_color=BG_LIGHT,
            button_color=PRIMARY,
            button_hover_color=PRIMARY_HOVER,
            font=ctk.CTkFont(size=12, family="Helvetica"),
            text_color=TEXT_PRIMARY,
            command=lambda _value: self.refresh_cars()
        )
        status_menu.grid(row=0, column=2, padx=10, pady=14)

        clear_btn = ctk.CTkButton(
            controls,
            text="Clear",
            width=70,
            height=38,
            fg_color="transparent",
            hover_color=BG_CARD_HOVER,
            text_color=TEXT_SECONDARY,
            font=ctk.CTkFont(size=12, family="Helvetica"),
            corner_radius=6,
            border_color=BORDER,
            border_width=1,
            command=self._clear_filters
        )
        clear_btn.grid(row=0, column=3, padx=(10, 16), pady=14)

        # Scrollable car grid — fills remaining vertical space
        self.cars_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=BG_LIGHT,
            scrollbar_button_hover_color=BORDER,
            width=1000
        )
        self.cars_frame.grid(row=2, column=0, sticky="nsew", padx=PAGE_PAD_X, pady=(0, 4))
        # The internal canvas column must expand so cards fill the full width
        self.cars_frame.grid_columnconfigure(0, weight=1)

        # Status label at the very bottom
        self.message_label = ctk.CTkLabel(
            self,
            text="Ready",
            font=ctk.CTkFont(size=12, family="Helvetica"),
            text_color=TEXT_SECONDARY
        )
        self.message_label.grid(row=3, column=0, sticky="w", padx=PAGE_PAD_X, pady=(2, 10))

    # ══════════════════════════════════════════════════════════════
    # State & Rendering
    # ══════════════════════════════════════════════════════════════

    def _on_search_change(self):
        if self._search_timer:
            self.after_cancel(self._search_timer)
        self._search_timer = self.after(250, self.refresh_cars)

    def _clear_filters(self):
        self.search_var.set("")
        self.category_var.set("all")
        self.status_var.set("all")
        self.refresh_cars()

    def refresh_cars(self):
        """Reload and render car cards."""
        self._set_message("Loading cars...", TEXT_MUTED)
        self.update_idletasks()
        self.cars = CarService.get_all(
            search=self.search_var.get().strip(),
            category=self.category_var.get(),
            status=self.status_var.get()
        )
        self._render_cars()
        count = len(self.cars)
        self._set_message(f"{count} car{'s' if count != 1 else ''} shown", TEXT_SECONDARY)

    def _render_cars(self):
        """Render cars in a responsive card grid."""
        for widget in self.cars_frame.winfo_children():
            widget.destroy()

        self.image_refs.clear()

        # Always reconfigure 3 equal columns so they span the full frame width
        for col in range(3):
            self.cars_frame.grid_columnconfigure(col, weight=1, uniform="cars")

        if not self.cars:
            hint = "Add a car to start building your fleet." if self.is_admin else "Check back soon for new additions."
            empty = EmptyState(
                self.cars_frame,
                icon="◇",
                title="No cars found",
                subtitle=hint,
            )
            empty.grid(row=0, column=0, sticky="nsew", pady=40, padx=40, columnspan=3)
            return

        for index, car in enumerate(self.cars):
            row = index // 3
            column = index % 3
            self._create_car_card(car, row, column)

    # ══════════════════════════════════════════════════════════════
    # Car Card
    # ══════════════════════════════════════════════════════════════

    def _create_car_card(self, car: Dict, row: int, column: int):
        """Create one car card — luxury styling with subtle border."""
        card = ctk.CTkFrame(
            self.cars_frame,
            fg_color=BG_CARD,
            corner_radius=CARD_RADIUS,
            border_color=BORDER,
            border_width=1
        )
        card.grid(row=row, column=column, sticky="nsew", padx=8, pady=10)
        card.grid_columnconfigure(0, weight=1)

        def _open_details(selected=car):
            details_page = self.app.pages.get("car_details")
            if details_page:
                details_page.set_car(selected)
                self.app.show_page("car_details")

        def _card_click(_event, selected=car):
            _open_details(selected)
            return "break"

        card.bind("<Button-1>", _card_click)

        image_widget = self._build_image_widget(card, car.get("image_url"))
        image_widget.grid(row=0, column=0, sticky="ew", padx=16, pady=(18, 12))

        name = ctk.CTkLabel(
            card,
            text=f"{car['brand']} {car['model']}",
            font=font_label(size=15, bold=True),
            text_color=TEXT_PRIMARY
        )
        name.grid(row=1, column=0, sticky="w", padx=18, pady=(8, 0))

        details = ctk.CTkLabel(
            card,
            text=f"{car['year']} • {car['category'].title()} • {car['seats']} seats",
            font=ctk.CTkFont(size=12, family="Helvetica"),
            text_color=TEXT_SECONDARY
        )
        details.grid(row=2, column=0, sticky="w", padx=18, pady=(8, 0))

        plate = ctk.CTkLabel(
            card,
            text=f"{car['license_plate']} · ₹{car['daily_rate']:,.0f}/day",
            font=ctk.CTkFont(size=12, family="Helvetica"),
            text_color=PRIMARY
        )
        plate.grid(row=3, column=0, sticky="w", padx=18, pady=(8, 0))

        # Status chip
        status = StatusChip(card, text=car["status"], status_type="car")
        status.grid(row=4, column=0, sticky="w", padx=18, pady=(12, 12))

        actions = ctk.CTkFrame(card, fg_color="transparent")
        actions.grid(row=5, column=0, sticky="ew", padx=16, pady=(4, 18))

        if not self.is_admin:
            actions.grid_propagate(False)
            actions.grid_rowconfigure(0, minsize=32)
            actions.grid_columnconfigure(0, weight=1)

            book_button = ctk.CTkButton(
                actions,
                text="Book",
                height=32,
                fg_color=PRIMARY,
                hover_color=PRIMARY_HOVER,
                text_color=BG_DARK,
                font=ctk.CTkFont(size=11, weight="bold", family="Helvetica"),
                corner_radius=6,
                state="normal" if car["status"] in ("available", "rented") else "disabled",
                command=lambda selected=car: self._open_booking_dialog(selected)
            )
            book_button.grid(row=0, column=0, sticky="ew")
            book_button.bind("<Button-1>", lambda _e: "break")
        else:
            actions.grid_columnconfigure((0, 1, 2), weight=1)

            book_button = ctk.CTkButton(
                actions,
                text="Book",
                height=32,
                fg_color=PRIMARY,
                hover_color=PRIMARY_HOVER,
                text_color=BG_DARK,
                font=ctk.CTkFont(size=11, weight="bold", family="Helvetica"),
                corner_radius=6,
                state="normal" if car["status"] in ("available", "rented") else "disabled",
                command=lambda selected=car: self._open_booking_dialog(selected)
            )
            book_button.grid(row=0, column=0, sticky="ew", padx=(0, 6))

            edit_button = ctk.CTkButton(
                actions,
                text="Edit",
                height=32,
                fg_color=BG_LIGHT,
                hover_color=BORDER,
                text_color=TEXT_PRIMARY,
                font=ctk.CTkFont(size=11, family="Helvetica"),
                corner_radius=6,
                command=lambda selected=car: self._open_edit_dialog(selected)
            )
            edit_button.grid(row=0, column=1, sticky="ew", padx=6)

            delete_button = ctk.CTkButton(
                actions,
                text="Delete",
                height=32,
                fg_color="transparent",
                hover_color=ACCENT_ERROR,
                text_color=ACCENT_ERROR,
                font=ctk.CTkFont(size=11, weight="bold", family="Helvetica"),
                corner_radius=6,
                border_color=ACCENT_ERROR,
                border_width=1,
                command=lambda selected=car: self._delete_car(selected)
            )
            delete_button.grid(row=0, column=2, sticky="ew", padx=(6, 0))

            book_button.bind("<Button-1>", lambda _e: "break")
            edit_button.bind("<Button-1>", lambda _e: "break")
            delete_button.bind("<Button-1>", lambda _e: "break")

        apply_card_hover(card)

    def _build_image_widget(self, parent, image_path: Optional[str]):
        """Build an image preview or fallback placeholder."""
        ctk_image = get_cached_image(image_path, 240, 155)
        if ctk_image is not None:
            self.image_refs.append(ctk_image)
            return ctk.CTkLabel(parent, text="", image=ctk_image, height=165)

        placeholder = ctk.CTkFrame(parent, fg_color=BG_LIGHT, corner_radius=8, height=165)
        placeholder.grid_propagate(False)
        placeholder.grid_columnconfigure(0, weight=1)
        placeholder.grid_rowconfigure(0, weight=1)

        icon = ctk.CTkLabel(
            placeholder,
            text="◆",
            font=ctk.CTkFont(size=28),
            text_color=BORDER_LIGHT
        )
        icon.grid(row=0, column=0)

        return placeholder

    # ══════════════════════════════════════════════════════════════
    # Dialog Handlers
    # ══════════════════════════════════════════════════════════════

    def _open_add_dialog(self):
        self._open_car_dialog()

    def _open_edit_dialog(self, car: Dict):
        self._open_car_dialog(car)

    def _open_booking_dialog(self, car: Dict):
        """Open the booking form for a selected car — luxury styling."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Book Car")
        dialog.geometry("460x540")
        dialog.resizable(False, False)
        dialog.configure(fg_color=BG_DARK)
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()

        form = BookingForm(dialog, car)
        form.pack(fill="both", expand=True)
        form.on_cancel = dialog.destroy
        form.on_confirm = lambda values: self._create_booking(dialog, form, car, values)

    def _open_car_dialog(self, car: Optional[Dict] = None):
        """Open add/edit car dialog — luxury styling."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Edit Car" if car else "Add Car")
        dialog.geometry("520x660")
        dialog.resizable(False, False)
        dialog.configure(fg_color=BG_DARK)
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()

        form = CarForm(dialog, car)
        form.pack(fill="both", expand=True)

        form.on_cancel = dialog.destroy
        form.on_save = lambda values: self._save_car(dialog, form, values, car)

    # ══════════════════════════════════════════════════════════════
    # Actions
    # ══════════════════════════════════════════════════════════════

    def _save_car(self, dialog, form, values: Dict, car: Optional[Dict]):
        if car:
            success, message = CarService.update(car["id"], values)
        else:
            success, message = CarService.create(values)

        if success:
            dialog.destroy()
            self._set_message(message, ACCENT_SUCCESS)
            self.refresh_cars()
        else:
            form.set_error(message)

    def _delete_car(self, car: Dict):
        ConfirmActionDialog(
            self,
            title="Delete Car?",
            message=f"{car['brand']} {car['model']} will be removed from the fleet.",
            confirm_text="Delete",
            confirm_color=ACCENT_ERROR,
            on_confirm=lambda: self._perform_delete_car(car)
        )

    def _perform_delete_car(self, car: Dict):
        self._set_message("Deleting car...", TEXT_MUTED)
        self.update_idletasks()
        success, message = CarService.delete(car["id"])
        self.refresh_cars()
        self._set_message(message, ACCENT_SUCCESS if success else ACCENT_ERROR)

    def _create_booking(self, dialog, form, car: Dict, values: Dict):
        success, message, booking = BookingService.create_booking(
            user_id=Session.get_user_id(),
            car_id=car["id"],
            start_date_text=values["start_date"],
            end_date_text=values["end_date"],
            pickup_location=values["pickup_location"],
            dropoff_location=values["dropoff_location"]
        )

        if not success:
            form.set_error(message)
            return

        dialog.destroy()
        self.refresh_cars()
        self._set_message(message, ACCENT_SUCCESS)
        BookingConfirmationDialog(self, booking)

    def _set_message(self, message: str, color: str):
        self.message_label.configure(text=message, text_color=color)
