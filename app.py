"""Main application window with sidebar navigation."""

import customtkinter as ctk
from typing import Dict

from database import db
from theme.colors import *
from ui.widgets.sidebar import Sidebar
from ui.pages.base_page import BasePage
from ui.pages.login_page import LoginPage
from ui.pages.register_page import RegisterPage
from ui.pages.landing_page import LandingPage
from utils.auth import Session
from services.demo_data_service import DemoDataService


class CarBookingApp(ctk.CTk):
    """Main application window."""

    def __init__(self):
        super().__init__()

        # Configure main window
        self.title("LuxuryDrive Booking System")
        self.geometry("1200x700")
        self.minsize(980, 620)
        self.resizable(True, True)

        # Configure CustomTkinter appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Initialize database used by services.
        self.db = db
        self._connect_database()

        # Store pages
        self.pages: Dict[str, BasePage] = {}
        self.current_page: str = ""

        # Auth state
        self.is_authenticated = False

        # Setup UI
        self._setup_ui()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _connect_database(self):
        """Connect to the database using environment variables from .env"""
        if not self.db.connect():
            raise RuntimeError("Failed to connect to database")

        if not self.db.initialize_database():
            raise RuntimeError("Failed to initialize database")

        DemoDataService.seed()

    def _setup_ui(self):
        """Setup the UI components."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Create auth container
        self.auth_container = ctk.CTkFrame(self, fg_color=BG_DARK)
        self.auth_container.grid(row=0, column=0, sticky="nsew")
        self.auth_container.grid_rowconfigure(0, weight=1)
        self.auth_container.grid_columnconfigure(0, weight=1)

        # Landing page
        self.landing_page = LandingPage(
            self.auth_container,
            self,
            on_get_started=self._on_get_started
        )
        self.landing_page.place(relx=0, rely=0, relwidth=1, relheight=1)

        # Login page (hidden initially)
        self.login_page = LoginPage(
            self.auth_container,
            self,
            on_login_success=self._on_login_success
        )
        self.login_page.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.login_page.lower()

        # Register page (hidden initially)
        self.register_page = RegisterPage(
            self.auth_container,
            self,
            on_register_success=self._on_register_success
        )
        self.register_page.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.register_page.lower()

        # Main app container (hidden initially)
        self.main_container = ctk.CTkFrame(self, fg_color=BG_DARK)
        self.main_container.grid(row=0, column=0, sticky="nsew")
        self.main_container.grid_remove()

        # Setup main app UI
        self._setup_main_ui()

    def _setup_main_ui(self):
        """Setup the main app UI with sidebar."""
        # Get navigation items based on user role
        nav_items = self._get_nav_items_for_user()

        self.sidebar = Sidebar(
            self.main_container,
            items=nav_items,
            on_select=self._on_navigate
        )
        # Keep geometry management consistent: use grid for both sidebar and content_frame
        self.main_container.grid_columnconfigure(0, weight=0)
        self.main_container.grid_columnconfigure(1, weight=1)
        self.sidebar.grid(row=0, column=0, sticky="nsw")

        # Content area — fills all remaining space (use grid consistently with child pages)
        self.content_frame = ctk.CTkFrame(
            self.main_container,
            fg_color=BG_MEDIUM,
            corner_radius=0
        )
        # Replace pack with grid to avoid geometry-manager conflicts with page.grid()
        self.content_frame.grid(row=0, column=1, sticky="nsew")
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(1, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

        # Initialize placeholder pages
        self._init_pages()

    def _get_nav_items_for_user(self):
        """Get navigation items based on current user role."""
        user = Session.get_current_user()
        is_admin = user and user.get("role") == "admin" if user else False

        if is_admin:
            return [
                {"id": "dashboard", "label": "Dashboard"},
                {"id": "browse_cars", "label": "Manage Cars"},
                {"id": "bookings_admin", "label": "Bookings"},
                {"id": "users_admin", "label": "Users"},
                {"id": "profile", "label": "Profile"},
                {"id": "logout", "label": "Logout"},
            ]
        else:
            return [
                {"id": "dashboard", "label": "Dashboard"},
                {"id": "browse_cars", "label": "Browse Cars"},
                {"id": "my_bookings", "label": "My Bookings"},
                {"id": "profile", "label": "Profile"},
                {"id": "logout", "label": "Logout"},
            ]

    def _init_pages(self):
        """Initialize pages that the user has access to."""
        from ui.pages.browse_cars_page import BrowseCarsPage
        from ui.pages.home_page import HomePage
        from ui.pages.my_bookings_page import MyBookingsPage
        from ui.pages.placeholder_page import PlaceholderPage
        from ui.pages.car_details_page import CarDetailsPage

        user = Session.get_current_user()
        is_admin = user and user.get("role") == "admin" if user else False

        # Dashboard page (available to all)
        self.pages["dashboard"] = HomePage(self.content_frame, self)

        # Car details page (available to all roles)
        self.pages["car_details"] = CarDetailsPage(self.content_frame, self)

        if is_admin:
            # Admin pages
            self.pages["browse_cars"] = BrowseCarsPage(self.content_frame, self, is_admin=True)
            self.pages["bookings_admin"] = PlaceholderPage(
                self.content_frame, self, "Bookings Management"
            )
            self.pages["users_admin"] = PlaceholderPage(
                self.content_frame, self, "Users Management"
            )
        else:
            # Customer pages
            self.pages["browse_cars"] = BrowseCarsPage(self.content_frame, self, is_admin=False)
            self.pages["my_bookings"] = MyBookingsPage(self.content_frame, self)

        # Profile page (available to all)
        self.pages["profile"] = PlaceholderPage(self.content_frame, self, "Profile")

        for page in self.pages.values():
            page.grid(row=0, column=0, sticky="nsew")

    def _on_get_started(self):
        """Switch from landing page to login page."""
        self.landing_page.lower()
        self.login_page.lift()

    def show_register_page(self):
        """Show the register page in auth container."""
        self.login_page.lower()
        self.register_page.lift()

    def show_login_page(self):
        """Show the login page in auth container."""
        self.register_page.lower()
        self.login_page.lift()

    def _on_login_success(self):
        """Handle successful login."""
        self.is_authenticated = True
        # Rebuild main UI with role-specific navigation
        if self.main_container.winfo_exists():
            self.main_container.destroy()
        self.main_container = ctk.CTkFrame(self, fg_color=BG_DARK)
        self.main_container.grid(row=0, column=0, sticky="nsew")
        
        self.pages = {}
        self._setup_main_ui()
        
        self.auth_container.grid_remove()
        self.main_container.grid()
        self.show_page("dashboard")
        self.sidebar.set_active("dashboard")

    def _on_register_success(self):
        """Handle successful registration - switch to login."""
        self.show_login_page()

    def _on_navigate(self, page_id: str):
        """Handle navigation."""
        if page_id == "logout":
            self._confirm_logout()
        else:
            self.show_page(page_id)

    def _confirm_logout(self):
        """Ask for confirmation before logging out."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Log Out")
        dialog.geometry("360x220")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        dialog.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            dialog,
            text="Log out?",
            font=ctk.CTkFont(size=21, weight="bold"),
            text_color=TEXT_PRIMARY
        )
        title.grid(row=0, column=0, sticky="w", padx=24, pady=(24, 8))

        message = ctk.CTkLabel(
            dialog,
            text="You can sign back in anytime.",
            font=ctk.CTkFont(size=14),
            text_color=TEXT_SECONDARY
        )
        message.grid(row=1, column=0, sticky="w", padx=24, pady=(0, 20))

        actions = ctk.CTkFrame(dialog, fg_color="transparent")
        actions.grid(row=2, column=0, sticky="ew", padx=24, pady=(12, 24))
        actions.grid_columnconfigure((0, 1), weight=1)

        stay = ctk.CTkButton(
            actions,
            text="Stay",
            height=38,
            fg_color=BG_LIGHT,
            hover_color=BORDER,
            command=dialog.destroy
        )
        stay.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        logout = ctk.CTkButton(
            actions,
            text="Log Out",
            height=38,
            fg_color=ACCENT_ERROR,
            hover_color="#C62828",
            command=lambda: (dialog.destroy(), self._on_logout())
        )
        logout.grid(row=0, column=1, sticky="ew", padx=(8, 0))

    def _on_logout(self):
        """Handle logout."""
        Session.logout()
        self.is_authenticated = False
        self.main_container.grid_remove()
        self.auth_container.grid()
        self.landing_page.lift()
        self.login_page.lower()
        self.register_page.lower()

    def _on_close(self):
        """Close resources before exiting the desktop app."""
        self.db.close()
        self.destroy()

    def show_page(self, page_id: str):
        """Show a specific page."""
        if page_id not in self.pages:
            return

        if self.current_page and self.current_page in self.pages:
            self.pages[self.current_page].on_hide()
            self.pages[self.current_page].grid_remove()

        self.pages[page_id].grid()
        self.pages[page_id].lift()
        self.pages[page_id].update_idletasks()
        self.pages[page_id].on_show()

        self.current_page = page_id
        if page_id in self.sidebar.buttons:
            self.sidebar.set_active(page_id)

    def run(self):
        """Start the application."""
        self.mainloop()


if __name__ == "__main__":
    app = CarBookingApp()
    app.run()
