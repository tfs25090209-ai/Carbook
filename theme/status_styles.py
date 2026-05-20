"""Shared status color and background mappings for car/booking status chips."""

from theme.colors import ACCENT_ERROR, ACCENT_SUCCESS, ACCENT_WARNING, BG_LIGHT, PRIMARY, TEXT_SECONDARY


# ═══════════════════════════════════════════════════════════════
# Car Status Styling
# ═══════════════════════════════════════════════════════════════

CAR_STATUS_TEXT_COLOR = {
    "available": ACCENT_SUCCESS,
    "rented": PRIMARY,
    "maintenance": ACCENT_WARNING,
    "unavailable": ACCENT_ERROR,
}

CAR_STATUS_BG = {
    "available": "#12301E",
    "rented": "#241F0A",
    "maintenance": "#2D2300",
    "unavailable": "#2A0D0D",
}

# ═══════════════════════════════════════════════════════════════
# Booking Status Styling
# ═══════════════════════════════════════════════════════════════

BOOKING_STATUS_TEXT_COLOR = {
    "pending": ACCENT_WARNING,
    "confirmed": ACCENT_SUCCESS,
    "active": PRIMARY,
    "completed": TEXT_SECONDARY,
    "cancelled": ACCENT_ERROR,
}

BOOKING_STATUS_BG = {
    "pending": "#2D2A00",
    "confirmed": "#0D2A1A",
    "active": "#1A1A2D",
    "completed": BG_LIGHT,
    "cancelled": "#2A0D0D",
}


# ═══════════════════════════════════════════════════════════════
# Public Helpers
# ═══════════════════════════════════════════════════════════════

def car_status_style(status: str) -> tuple[str, str]:
    """Return (text_color, background_color) for a given car status."""
    text = CAR_STATUS_TEXT_COLOR.get(status, TEXT_SECONDARY)
    bg = CAR_STATUS_BG.get(status, BG_LIGHT)
    return text, bg


def booking_status_style(status: str) -> tuple[str, str]:
    """Return (text_color, background_color) for a given booking status."""
    text = BOOKING_STATUS_TEXT_COLOR.get(status, TEXT_SECONDARY)
    bg = BOOKING_STATUS_BG.get(status, BG_LIGHT)
    return text, bg
