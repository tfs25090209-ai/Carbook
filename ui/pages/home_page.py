"""Home/Dashboard page."""

import customtkinter as ctk
from database import db
from services.car_service import CarService
from ui.pages.base_page import BasePage
from utils.auth import Session
from theme.colors import *
from theme.typography import font_heading_lg, font_body_secondary, font_heading_md, font_label
from utils.image_loader import get_cached_image
from utils.ui_helpers import apply_card_hover


class HomePage(BasePage):
    """Home page with dashboard overview."""

    def __init__(self, master, app, **kwargs):
        super().__init__(master, app, **kwargs)
        self.stat_cards = []
        self.cars_container = None
        self._setup_ui()

    def _setup_ui(self):
        """Setup the home page UI."""
        # Use grid layout for proper scaling with parent content_frame
        self.grid_rowconfigure(0, weight=0)  # welcome section
        self.grid_rowconfigure(1, weight=0)  # stats section
        self.grid_rowconfigure(2, weight=1)  # featured cars (expands to fill space)
        self.grid_columnconfigure(0, weight=1)

        # Welcome section
        self._create_welcome_section()

        # Stats section
        self._create_stats_section()

        # Featured cars section
        self._create_featured_cars_section()

    def _create_welcome_section(self):
        """Create welcome message section."""
        welcome_frame = ctk.CTkFrame(self, fg_color="transparent")
        welcome_frame.grid(row=0, column=0, sticky="ew", padx=PAGE_PAD_X, pady=(PAGE_PAD_Y, 12))
        welcome_frame.grid_columnconfigure(0, weight=1)

        # Get user name
        user = Session.get_current_user()
        user_name = user.get("full_name", "User") if user else "User"

        # Welcome title
        self.welcome_label = ctk.CTkLabel(
            welcome_frame,
            text=f"Welcome back, {user_name}!",
            font=font_heading_lg(bold=True),
            text_color=TEXT_PRIMARY
        )
        self.welcome_label.grid(row=0, column=0, sticky="w")

        # Subtitle
        subtitle_label = ctk.CTkLabel(
            welcome_frame,
            text="Your luxury driving experience awaits",
            font=font_body_secondary(size=14),
            text_color=TEXT_SECONDARY
        )
        self.subtitle_label = subtitle_label
        # Slightly more breathing room above to feel more premium
        self.subtitle_label.grid(row=1, column=0, sticky="w", pady=(8, 0))

    def _create_stats_section(self):
        """Create statistics cards section."""
        stats_container = ctk.CTkFrame(self, fg_color="transparent")
        # More even vertical rhythm and card balance across the row
        stats_container.grid(row=1, column=0, sticky="ew", padx=PAGE_PAD_X, pady=(10, 18))
        for column in range(3):
            # Ensure all 3 cards share available width consistently
            stats_container.grid_columnconfigure(column, weight=1, uniform="stats")

        stats = self._get_stats()

        # Create cards
        for index, stat in enumerate(stats):
            self._create_stat_card(stats_container, stat, index)

    def _create_stat_card(self, parent, stat, column):
        """Create a statistics card widget."""
        card = ctk.CTkFrame(
            parent,
            fg_color=BG_CARD,
            corner_radius=CARD_RADIUS,
            border_color=BORDER,
            border_width=1
        )
        # Balanced horizontal padding across all 3 cards (not just first two)
        card.grid(row=0, column=column, sticky="nsew", padx=10)
        card.grid_columnconfigure(0, weight=1)

        # Give the card a clean internal layout height distribution
        card.grid_rowconfigure(0, weight=0)
        card.grid_rowconfigure(1, weight=0)
        card.grid_rowconfigure(2, weight=0)

        # Icon with luxury accent background (badge)
        icon_outer = ctk.CTkFrame(
            card,
            fg_color="transparent",
            corner_radius=8,
            width=48,
            height=48
        )
        icon_outer.grid(row=0, column=0, sticky="w", padx=18, pady=(18, 8))
        icon_outer.grid_propagate(False)

        icon_frame = ctk.CTkFrame(
            icon_outer,
            fg_color=PRIMARY,
            corner_radius=7,
            width=40,
            height=40
        )
        icon_frame.place(relx=0.5, rely=0.5, anchor="center")
        icon_frame.grid_propagate(False)

        icon_label = ctk.CTkLabel(
            icon_frame,
            text=stat["icon"],
            font=ctk.CTkFont(size=17, weight="bold"),
            text_color=BG_DARK
        )
        icon_label.place(relx=0.5, rely=0.5, anchor="center")

        # Value (more premium emphasis via value font helper)
        value_label = ctk.CTkLabel(
            card,
            text=stat["value"],
            font=ctk.CTkFont(size=26, weight="bold", family="Helvetica"),
            text_color=TEXT_PRIMARY
        )
        value_label.grid(row=1, column=0, sticky="w", padx=20, pady=(2, 0))

        # Title with clearer visual hierarchy
        title_label = ctk.CTkLabel(
            card,
            text=stat["title"],
            font=ctk.CTkFont(size=12, family="Helvetica"),
            text_color=TEXT_SECONDARY
        )
        title_label.grid(row=2, column=0, sticky="w", padx=20, pady=(6, 20))

        self.stat_cards.append({
            "icon": icon_label,
            "value": value_label,
            "title": title_label,
        })

    def _create_featured_cars_section(self):
        """Create featured cars section."""
        section_frame = ctk.CTkFrame(self, fg_color="transparent")
        section_frame.grid(row=2, column=0, sticky="ew", padx=PAGE_PAD_X, pady=(8, 30))
        section_frame.grid_columnconfigure(0, weight=1)

        # Section header
        header_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        header_frame.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(
            header_frame,
            text="Featured Vehicles",
            font=font_heading_md(bold=True),
            text_color=TEXT_PRIMARY
        )
        title_label.grid(row=0, column=0, sticky="w")

        # See all button - luxury style
        see_all_btn = ctk.CTkButton(
            header_frame,
            text="Browse All",
            fg_color="transparent",
            text_color=PRIMARY,
            hover_color=BG_CARD_HOVER,
            font=ctk.CTkFont(size=12, family="Helvetica"),
            width=90,
            height=28,
            border_width=1,
            border_color=PRIMARY,
            command=lambda: self.app.show_page("browse_cars")
        )
        see_all_btn.grid(row=0, column=1, sticky="e")

        # Cars container — 4 equal columns
        cars_container = ctk.CTkFrame(section_frame, fg_color="transparent")
        cars_container.grid(row=1, column=0, sticky="ew")
        for column in range(4):
            cars_container.grid_columnconfigure(column, weight=1, uniform="cars")
        self.cars_container = cars_container

        self._render_featured_cars()

    def _create_car_card(self, parent, car, column):
        """Create a car card widget."""
        card = ctk.CTkFrame(
            parent,
            fg_color=BG_CARD,
            corner_radius=CARD_RADIUS,
            border_color=BORDER,
            border_width=1
        )
        card.grid(row=0, column=column, sticky="nsew", padx=(0, 12) if column < 3 else 0)
        card.grid_columnconfigure(0, weight=1)

        image_frame = ctk.CTkFrame(card, fg_color=BG_MEDIUM, corner_radius=6, height=100)
        image_frame.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 8))
        image_frame.grid_propagate(False)
        image_frame.grid_columnconfigure(0, weight=1)
        image_frame.grid_rowconfigure(0, weight=1)

        ctk_image = get_cached_image(car.get("image_url"), 160, 100)
        if ctk_image is not None:
            image_label = ctk.CTkLabel(image_frame, text="", image=ctk_image)
        else:
            image_label = ctk.CTkLabel(
                image_frame,
                text="⬡",
                font=ctk.CTkFont(size=36),
                text_color=PRIMARY
            )
        image_label.grid(row=0, column=0)

        name_label = ctk.CTkLabel(
            card,
            text=f"{car['brand']} {car['model']}",
            font=font_label(size=15, bold=True),
            text_color=TEXT_PRIMARY
        )
        name_label.grid(row=1, column=0, sticky="w", padx=16)

        price_label = ctk.CTkLabel(
            card,
            text=car["price"],
            font=ctk.CTkFont(size=12, family="Helvetica"),
            text_color=PRIMARY
        )
        price_label.grid(row=2, column=0, sticky="w", padx=16, pady=(6, 16))

        apply_card_hover(card)

    def _get_stats(self):
        """Return dashboard cards tailored by role."""
        user_id = Session.get_user_id()
        # Premium minimal icon glyphs (single char per card, luxury dark + gold aesthetic)
        # Note: This keeps the existing “icon as text label” mechanism intact.
        admin_icons = {
            "Luxury Fleet": "⧉",          # structured grid
            "Available": "⟡",            # diamond/check-like minimal
            "Active Bookings": "⟲",     # loop/active pulse
        }

        user_icons = {
            "Total Bookings": "⟲",
            "Active Rentals": "⟡",
            "Available Cars": "⧉",
        }

        def _count(query: str, params: tuple = ()) -> int:
            row = db.fetch_one(query, params) if params else db.fetch_one(query)
            return int(row["count"]) if row else 0

        if Session.is_admin():
            total_cars = _count("SELECT COUNT(*) AS count FROM cars")
            available = _count("SELECT COUNT(*) AS count FROM cars WHERE status = %s", ("available",))
            active = _count(
                "SELECT COUNT(*) AS count FROM bookings WHERE status IN (%s, %s, %s)",
                ("pending", "confirmed", "active"),
            )
            return [
                {"title": "Luxury Fleet", "value": str(total_cars), "icon": admin_icons["Luxury Fleet"]},
                {"title": "Available", "value": str(available), "icon": admin_icons["Available"]},
                {"title": "Active Bookings", "value": str(active), "icon": admin_icons["Active Bookings"]},
            ]

        total = _count(
            "SELECT COUNT(*) AS count FROM bookings WHERE user_id = %s",
            (user_id,),
        ) if user_id else 0

        active = _count(
            "SELECT COUNT(*) AS count FROM bookings WHERE user_id = %s AND status IN (%s, %s, %s)",
            (user_id, "pending", "confirmed", "active"),
        ) if user_id else 0

        available = _count("SELECT COUNT(*) AS count FROM cars WHERE status = %s", ("available",))
        return [
            {"title": "Total Bookings", "value": str(total), "icon": user_icons["Total Bookings"]},
            {"title": "Active Rentals", "value": str(active), "icon": user_icons["Active Rentals"]},
            {"title": "Available Cars", "value": str(available), "icon": user_icons["Available Cars"]},
        ]

    def _render_featured_cars(self):
        """Render the top luxury cars from MySQL."""
        if not self.cars_container:
            return

        for widget in self.cars_container.winfo_children():
            widget.destroy()

        featured_cars = CarService.get_all(status="available")[:4]
        if not featured_cars:
            featured_cars = CarService.get_all()[:4]

        for index, car in enumerate(featured_cars):
            self._create_car_card(self.cars_container, {
                "brand": car["brand"],
                "model": car["model"],
                "price": f"₹{car['daily_rate']:,.0f}/day",
                "image_url": car.get("image_url"),
            }, index)

    def on_show(self):
        """Called when page is shown."""
        user = Session.get_current_user()
        user_name = user.get("full_name", "User") if user else "User"
        if Session.is_admin():
            self.welcome_label.configure(text=f"Admin Dashboard, {user_name}")
            self.subtitle_label.configure(text="Fleet management and reservation overview.")
        else:
            self.welcome_label.configure(text=f"Welcome back, {user_name}!")
            self.subtitle_label.configure(text="Your luxury driving experience awaits.")

        for index, stat in enumerate(self._get_stats()):
            if index < len(self.stat_cards):
                self.stat_cards[index]["value"].configure(text=stat["value"])
                self.stat_cards[index]["title"].configure(text=stat["title"])
        self._render_featured_cars()
