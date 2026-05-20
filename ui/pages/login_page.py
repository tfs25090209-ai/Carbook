"""Login page for Car Booking System — Luxury Edition."""

import customtkinter as ctk
from services.auth_service import AuthService
from utils.auth import Session
from theme.colors import *


class LoginPage(ctk.CTkFrame):
    """Login page with form authentication."""

    def __init__(self, master, app, on_login_success, **kwargs):
        super().__init__(master, **kwargs)
        self.app = app
        self.on_login_success = on_login_success
        self._setup_ui()

    def _setup_ui(self):
        """Setup the login page UI."""
        self.configure(fg_color=BG_DARK)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Center card — subtle luxury border
        card = ctk.CTkFrame(
            self,
            fg_color=BG_CARD,
            corner_radius=CARD_RADIUS,
            border_color=BORDER,
            border_width=1
        )
        card.grid(row=0, column=0, padx=20, pady=20)
        card.grid_rowconfigure(10, weight=1)

        # Elegant brand mark
        brand_frame = ctk.CTkFrame(card, fg_color="transparent")
        brand_frame.grid(row=0, column=0, pady=(32, 12), padx=40)

        brand_mark = ctk.CTkLabel(
            brand_frame,
            text="◆",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=PRIMARY
        )
        brand_mark.pack()

        # Title
        title = ctk.CTkLabel(
            card,
            text="Welcome Back",
            font=ctk.CTkFont(size=26, weight="bold", family="Helvetica"),
            text_color=TEXT_PRIMARY
        )
        title.grid(row=1, column=0, pady=(0, 4), padx=40)

        # Subtitle
        subtitle = ctk.CTkLabel(
            card,
            text="Sign in to your account",
            font=ctk.CTkFont(size=13, family="Helvetica"),
            text_color=TEXT_SECONDARY
        )
        subtitle.grid(row=2, column=0, pady=(0, 24), padx=40)

        # Username or email
        username_label = ctk.CTkLabel(
            card,
            text="Username or Email",
            font=ctk.CTkFont(size=11, family="Helvetica"),
            text_color=TEXT_SECONDARY
        )
        username_label.grid(row=3, column=0, padx=40, pady=(0, 6), sticky="w")

        self.username_entry = ctk.CTkEntry(
            card,
            width=300,
            height=44,
            fg_color=BG_LIGHT,
            border_color=BORDER,
            border_width=1,
            text_color=TEXT_PRIMARY,
            placeholder_text="Enter username or email",
            placeholder_text_color=TEXT_MUTED,
            font=ctk.CTkFont(size=13, family="Helvetica")
        )
        self.username_entry.grid(row=4, column=0, padx=40, pady=(0, 16))

        # Password
        password_label = ctk.CTkLabel(
            card,
            text="Password",
            font=ctk.CTkFont(size=11, family="Helvetica"),
            text_color=TEXT_SECONDARY
        )
        password_label.grid(row=5, column=0, padx=40, pady=(0, 6), sticky="w")

        self.password_entry = ctk.CTkEntry(
            card,
            width=300,
            height=44,
            fg_color=BG_LIGHT,
            border_color=BORDER,
            border_width=1,
            text_color=TEXT_PRIMARY,
            placeholder_text="Enter password",
            placeholder_text_color=TEXT_MUTED,
            font=ctk.CTkFont(size=13, family="Helvetica")
        )
        self.password_entry.grid(row=6, column=0, padx=40, pady=(0, 12))

        # Error message
        self.error_label = ctk.CTkLabel(
            card,
            text="",
            font=ctk.CTkFont(size=12, family="Helvetica"),
            text_color=ACCENT_ERROR
        )
        self.error_label.grid(row=7, column=0, padx=40, pady=(0, 12))

        # Login button — dark text on gold for contrast
        login_btn = ctk.CTkButton(
            card,
            text="Sign In",
            width=300,
            height=46,
            fg_color=PRIMARY,
            hover_color=PRIMARY_HOVER,
            text_color=BG_DARK,  # Dark text on gold
            font=ctk.CTkFont(size=13, weight="bold", family="Helvetica"),
            corner_radius=CARD_RADIUS,
            command=self._on_login
        )
        login_btn.grid(row=8, column=0, padx=40, pady=(8, 24))

        # Divider
        divider = ctk.CTkFrame(card, fg_color=BORDER, height=1, width=300)
        divider.grid(row=9, column=0, pady=(0, 20))

        # Register link
        register_frame = ctk.CTkFrame(card, fg_color="transparent")
        register_frame.grid(row=10, column=0, padx=40, pady=(0, 32))

        register_label = ctk.CTkLabel(
            register_frame,
            text="Don't have an account?",
            font=ctk.CTkFont(size=12, family="Helvetica"),
            text_color=TEXT_MUTED
        )
        register_label.pack(side="left", padx=(0, 6))

        register_btn = ctk.CTkButton(
            register_frame,
            text="Sign Up",
            fg_color="transparent",
            text_color=PRIMARY,
            hover_color=BG_CARD_HOVER,
            font=ctk.CTkFont(size=12, weight="bold", family="Helvetica"),
            width=60,
            command=self._on_register_click
        )
        register_btn.pack(side="left")

        # Bind Enter key
        self.password_entry.bind("<Return>", lambda e: self._on_login())

    def _on_login(self):
        """Handle login button click."""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        if not username or not password:
            self.error_label.configure(text="Please enter username and password")
            return

        success, result = AuthService.login(username, password)

        if success:
            Session.login(result)
            self.error_label.configure(text="")
            self.username_entry.delete(0, "end")
            self.password_entry.delete(0, "end")
            self.on_login_success()
        else:
            self.error_label.configure(text=result)

    def _on_register_click(self):
        """Switch to register page."""
        self.app.show_register_page()

    def clear_fields(self):
        """Clear form fields."""
        self.username_entry.delete(0, "end")
        self.password_entry.delete(0, "end")
        self.error_label.configure(text="")