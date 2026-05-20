"""Registration page for Car Booking System — Luxury Edition."""

import customtkinter as ctk
from services.auth_service import AuthService
from theme.colors import *


class RegisterPage(ctk.CTkFrame):
    """Registration page with form validation."""

    def __init__(self, master, app, on_register_success, **kwargs):
        super().__init__(master, **kwargs)
        self.app = app
        self.on_register_success = on_register_success
        self._setup_ui()

    def _setup_ui(self):
        """Setup the register page UI."""
        self.configure(fg_color=BG_DARK)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Center card — luxury styling
        card = ctk.CTkScrollableFrame(
            self,
            fg_color=BG_CARD,
            corner_radius=CARD_RADIUS,
            border_color=BORDER,
            border_width=1,
            width=380,
            height=640,
            scrollbar_button_color=BG_LIGHT,
            scrollbar_button_hover_color=BORDER
        )
        card.grid(row=0, column=0, padx=20, pady=20)

        # Elegant brand mark
        brand_frame = ctk.CTkFrame(card, fg_color="transparent")
        brand_frame.grid(row=0, column=0, pady=(28, 8), padx=40)

        brand_mark = ctk.CTkLabel(
            brand_frame,
            text="◆",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=PRIMARY
        )
        brand_mark.pack()

        # Title
        title = ctk.CTkLabel(
            card,
            text="Create Account",
            font=ctk.CTkFont(size=24, weight="bold", family="Helvetica"),
            text_color=TEXT_PRIMARY
        )
        title.grid(row=1, column=0, pady=(8, 4), padx=40)

        subtitle = ctk.CTkLabel(
            card,
            text="Join the premium collection",
            font=ctk.CTkFont(size=13, family="Helvetica"),
            text_color=TEXT_SECONDARY
        )
        subtitle.grid(row=2, column=0, pady=(0, 24), padx=40)

        # Form field helper
        def create_field(row, label_text, placeholder, is_password=False):
            label = ctk.CTkLabel(
                card,
                text=label_text,
                font=ctk.CTkFont(size=11, family="Helvetica"),
                text_color=TEXT_SECONDARY
            )
            label.grid(row=row, column=0, padx=40, pady=(0, 5), sticky="w")

            entry = ctk.CTkEntry(
                card,
                width=300,
                height=44,
                fg_color=BG_LIGHT,
                border_color=BORDER,
                border_width=1,
                text_color=TEXT_PRIMARY,
                placeholder_text=placeholder,
                placeholder_text_color=TEXT_MUTED,
                font=ctk.CTkFont(size=13, family="Helvetica")
            )
            entry.grid(row=row + 1, column=0, padx=40, pady=(0, 12))

            if is_password:
                entry.configure(show="•")

            return entry

        # Form fields
        self.name_entry = create_field(3, "Full Name", "Enter full name")
        self.username_entry = create_field(5, "Username", "Choose a username")
        self.email_entry = create_field(7, "Email", "Enter your email")
        self.phone_entry = create_field(9, "Phone (optional)", "Enter phone number")
        self.password_entry = create_field(11, "Password", "Create a password", is_password=True)
        self.confirm_entry = create_field(13, "Confirm Password", "Confirm your password", is_password=True)

        # Error message
        self.error_label = ctk.CTkLabel(
            card,
            text="",
            font=ctk.CTkFont(size=12, family="Helvetica"),
            text_color=ACCENT_ERROR
        )
        self.error_label.grid(row=16, column=0, padx=40, pady=(0, 8))

        # Success message
        self.success_label = ctk.CTkLabel(
            card,
            text="",
            font=ctk.CTkFont(size=12, family="Helvetica"),
            text_color=ACCENT_SUCCESS
        )
        self.success_label.grid(row=17, column=0, padx=40, pady=(0, 12))

        # Register button — gold with dark text
        register_btn = ctk.CTkButton(
            card,
            text="Create Account",
            width=300,
            height=46,
            fg_color=PRIMARY,
            hover_color=PRIMARY_HOVER,
            text_color=BG_DARK,  # Dark text on gold
            font=ctk.CTkFont(size=13, weight="bold", family="Helvetica"),
            corner_radius=CARD_RADIUS,
            command=self._on_register
        )
        register_btn.grid(row=18, column=0, padx=40, pady=(8, 20))

        # Subtle divider
        divider = ctk.CTkFrame(card, fg_color=BORDER, height=1, width=300)
        divider.grid(row=19, column=0, pady=(0, 16))

        # Login link
        login_frame = ctk.CTkFrame(card, fg_color="transparent")
        login_frame.grid(row=20, column=0, padx=40, pady=(0, 28))

        login_label = ctk.CTkLabel(
            login_frame,
            text="Already have an account?",
            font=ctk.CTkFont(size=12, family="Helvetica"),
            text_color=TEXT_MUTED
        )
        login_label.pack(side="left", padx=(0, 6))

        login_btn = ctk.CTkButton(
            login_frame,
            text="Sign In",
            fg_color="transparent",
            text_color=PRIMARY,
            hover_color=BG_CARD_HOVER,
            font=ctk.CTkFont(size=12, weight="bold", family="Helvetica"),
            width=60,
            command=self._on_login_click
        )
        login_btn.pack(side="left")

        # Bind Enter key to register
        self.confirm_entry.bind("<Return>", lambda e: self._on_register())

    def _on_register(self):
        """Handle register button click."""
        full_name = self.name_entry.get().strip()
        username = self.username_entry.get().strip()
        email = self.email_entry.get().strip()
        phone = self.phone_entry.get().strip()
        password = self.password_entry.get()
        confirm = self.confirm_entry.get()

        # Clear previous messages
        self.error_label.configure(text="")
        self.success_label.configure(text="")

        # Validation
        if not full_name or not username or not email or not password:
            self.error_label.configure(text="All required fields are needed")
            return

        if password != confirm:
            self.error_label.configure(text="Passwords do not match")
            return

        if len(password) < 6:
            self.error_label.configure(text="Password must be at least 6 characters")
            return

        # Register user
        success, message = AuthService.register(
            username=username,
            email=email,
            password=password,
            full_name=full_name,
            phone=phone if phone else None
        )

        if success:
            self._clear_fields()
            self.success_label.configure(text="Account created. Redirecting...")
            self.after(1500, self.on_register_success)
        else:
            self.error_label.configure(text=message)

    def _on_login_click(self):
        """Switch to login page."""
        self.app.show_login_page()

    def _clear_fields(self):
        """Clear all form fields."""
        self.name_entry.delete(0, "end")
        self.username_entry.delete(0, "end")
        self.email_entry.delete(0, "end")
        self.phone_entry.delete(0, "end")
        self.password_entry.delete(0, "end")
        self.confirm_entry.delete(0, "end")
        self.error_label.configure(text="")
        self.success_label.configure(text="")