"""Landing page for Car Booking System — Luxury Edition."""

import customtkinter as ctk
from theme.colors import *


class LandingPage(ctk.CTkFrame):
    """Landing page shown before authentication."""

    def __init__(self, master, app, on_get_started, **kwargs):
        super().__init__(master, **kwargs)
        self.app = app
        self.on_get_started = on_get_started
        self._setup_ui()

    def _setup_ui(self):
        """Setup the landing page UI.

        This page is placed via place(relwidth=1, relheight=1) by the app,
        so it always fills its parent. Pack is used throughout; no grid/pack
        mixing occurs within any single container.
        """
        self.configure(fg_color=BG_DARK)

        # Subtle background accent line
        bg_accent = ctk.CTkFrame(self, fg_color=PRIMARY)
        bg_accent.place(relx=0.5, rely=0.35, anchor="center",
                        relwidth=0.6, relheight=0.01)
        bg_accent.lower()

        # Outer container — fills the page and centres the hero section
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True)

        # Hero section — pack children top-to-bottom, centred
        hero_frame = ctk.CTkFrame(container, fg_color="transparent")
        hero_frame.pack(expand=True, fill="both")

        # Brand diamond mark
        brand_frame = ctk.CTkFrame(hero_frame, fg_color="transparent")
        brand_frame.pack(pady=(0, 32))

        brand_mark = ctk.CTkLabel(
            brand_frame,
            text="◆",
            font=ctk.CTkFont(size=72, weight="bold"),
            text_color=PRIMARY
        )
        brand_mark.pack()

        # Title
        title = ctk.CTkLabel(
            hero_frame,
            text="LUXURYDRIVE",
            font=ctk.CTkFont(size=44, weight="bold", family="Helvetica"),
            text_color=TEXT_PRIMARY,
        )
        title.pack(pady=(0, 8))

        # Tagline
        tagline = ctk.CTkLabel(
            hero_frame,
            text="Premium Collection",
            font=ctk.CTkFont(size=13, family="Helvetica"),
            text_color=PRIMARY,
        )
        tagline.pack(pady=(0, 16))

        # Subtitle
        subtitle = ctk.CTkLabel(
            hero_frame,
            text="Exceptional vehicles for extraordinary journeys",
            font=ctk.CTkFont(size=16, family="Helvetica"),
            text_color=TEXT_SECONDARY
        )
        subtitle.pack(pady=(0, 48))

        # Features row — all pack, no mixing
        features_frame = ctk.CTkFrame(hero_frame, fg_color="transparent")
        features_frame.pack(pady=(0, 48))

        features = [
            ("◈", "Curated Fleet"),
            ("◉", "Elite Service"),
            ("◇", "Best Value"),
        ]

        for icon, text in features:
            feature_item = ctk.CTkFrame(features_frame, fg_color="transparent")
            feature_item.pack(side="left", padx=40)

            icon_label = ctk.CTkLabel(
                feature_item,
                text=icon,
                font=ctk.CTkFont(size=20),
                text_color=PRIMARY
            )
            icon_label.pack()

            text_label = ctk.CTkLabel(
                feature_item,
                text=text,
                font=ctk.CTkFont(size=12, family="Helvetica"),
                text_color=TEXT_SECONDARY
            )
            text_label.pack(pady=(8, 0))

        # CTA Button
        cta_btn = ctk.CTkButton(
            hero_frame,
            text="Begin Your Journey",
            width=220,
            height=52,
            fg_color=PRIMARY,
            hover_color=PRIMARY_HOVER,
            text_color=BG_DARK,
            font=ctk.CTkFont(size=14, weight="bold", family="Helvetica"),
            corner_radius=CARD_RADIUS,
            command=self.on_get_started
        )
        cta_btn.pack()

        # Elegant divider
        divider = ctk.CTkFrame(
            hero_frame,
            fg_color=BORDER,
            height=1,
            width=200
        )
        divider.pack(pady=(48, 12))

        # Footer
        footer = ctk.CTkLabel(
            hero_frame,
            text="© 2026 LuxuryDrive. All rights reserved.",
            font=ctk.CTkFont(size=11, family="Helvetica"),
            text_color=TEXT_MUTED
        )
        footer.pack()