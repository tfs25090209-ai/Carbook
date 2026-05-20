"""Typography tokens and helpers for consistent UI text styling."""

import customtkinter as ctk

# Font family is kept consistent to preserve the current theme feel.
_DEFAULT_FAMILY = "Helvetica"

# Size scale (kept within current app bounds; avoid overly large fonts)
HEADING_LG_SIZE = 26
HEADING_MD_SIZE = 20
HEADING_SM_SIZE = 18

BODY_SIZE = 13
BODY_SECONDARY_SIZE = 12
LABEL_SIZE = 12
BUTTON_SIZE = 12
VALUE_LG_SIZE = 26

# Weights (CTkFont accepts: "normal" / "bold")
WEIGHT_NORMAL = "normal"
WEIGHT_BOLD = "bold"


def font_heading_lg(bold: bool = True, family: str = _DEFAULT_FAMILY, size: int = HEADING_LG_SIZE) -> ctk.CTkFont:
    """Primary page heading."""
    return ctk.CTkFont(size=size, weight=WEIGHT_BOLD if bold else WEIGHT_NORMAL, family=family)


def font_heading_md(bold: bool = True, family: str = _DEFAULT_FAMILY, size: int = HEADING_MD_SIZE) -> ctk.CTkFont:
    """Section heading."""
    return ctk.CTkFont(size=size, weight=WEIGHT_BOLD if bold else WEIGHT_NORMAL, family=family)


def font_heading_sm(bold: bool = True, family: str = _DEFAULT_FAMILY, size: int = HEADING_SM_SIZE) -> ctk.CTkFont:
    """Component heading (cards/side areas)."""
    return ctk.CTkFont(size=size, weight=WEIGHT_BOLD if bold else WEIGHT_NORMAL, family=family)


def font_body(bold: bool = False, family: str = _DEFAULT_FAMILY, size: int = BODY_SIZE) -> ctk.CTkFont:
    """Main body text."""
    return ctk.CTkFont(size=size, weight=WEIGHT_BOLD if bold else WEIGHT_NORMAL, family=family)


def font_body_secondary(family: str = _DEFAULT_FAMILY, size: int = BODY_SECONDARY_SIZE) -> ctk.CTkFont:
    """Secondary body/tertiary labels."""
    return ctk.CTkFont(size=size, weight=WEIGHT_NORMAL, family=family)


def font_label(family: str = _DEFAULT_FAMILY, size: int = LABEL_SIZE, bold: bool = False) -> ctk.CTkFont:
    """Labels and metadata."""
    return ctk.CTkFont(size=size, weight=WEIGHT_BOLD if bold else WEIGHT_NORMAL, family=family)


def font_button(bold: bool = True, family: str = _DEFAULT_FAMILY, size: int = BUTTON_SIZE) -> ctk.CTkFont:
    """Buttons (kept consistent across the app)."""
    return ctk.CTkFont(size=size, weight=WEIGHT_BOLD if bold else WEIGHT_NORMAL, family=family)


def font_value_lg(bold: bool = True, family: str = _DEFAULT_FAMILY, size: int = VALUE_LG_SIZE) -> ctk.CTkFont:
    """Large numeric/value emphasis."""
    return ctk.CTkFont(size=size, weight=WEIGHT_BOLD if bold else WEIGHT_NORMAL, family=family)


# Spacing tokens (used sparingly with existing layout)
SPACE_4 = 4
SPACE_6 = 6
SPACE_8 = 8
SPACE_10 = 10
SPACE_12 = 12
SPACE_15 = 15
SPACE_18 = 18
