"""Centralized image loading, caching, and validation utilities."""

from pathlib import Path
from collections import OrderedDict
from typing import Optional, Tuple

import customtkinter as ctk

try:
    from PIL import Image, UnidentifiedImageError
    _PIL_AVAILABLE = True
except ImportError:
    _PIL_AVAILABLE = False
    Image = None
    UnidentifiedImageError = Exception


_VALID_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
_MAX_CACHE_SIZE = 64

_IMAGE_CACHE: OrderedDict = OrderedDict()


def _make_cache_key(path: str, width: int, height: int) -> Tuple:
    return (Path(path).resolve().as_posix().lower(), width, height)


def get_cached_image(path: Optional[str], width: int, height: int) -> Optional[ctk.CTkImage]:
    """Return a CTkImage from cache or load from disk.

    Returns None if the image cannot be loaded.
    Handles missing files, corrupt images, and unsupported formats gracefully.
    """
    if not _PIL_AVAILABLE or not path:
        return None

    key = _make_cache_key(path, width, height)

    if key in _IMAGE_CACHE:
        _IMAGE_CACHE.move_to_end(key)
        return _IMAGE_CACHE[key]

    resolved = Path(path)
    if not resolved.exists() or not resolved.is_file():
        return None

    try:
        pil_image = Image.open(resolved)
        pil_image.load()
        ctk_image = ctk.CTkImage(
            light_image=pil_image,
            dark_image=pil_image,
            size=(width, height),
        )
    except Exception:
        return None

    if len(_IMAGE_CACHE) >= _MAX_CACHE_SIZE:
        _IMAGE_CACHE.popitem(last=False)

    _IMAGE_CACHE[key] = ctk_image
    return ctk_image


def clear_image_cache():
    """Clear all cached images to free memory."""
    _IMAGE_CACHE.clear()


def get_cache_size() -> int:
    """Return number of entries currently in the image cache."""
    return len(_IMAGE_CACHE)


def validate_image_file(path: str) -> Tuple[bool, str]:
    """Check that path points to a valid, readable image file.

    Returns (is_valid, error_message).
    """
    if not path:
        return False, "No path provided"

    resolved = Path(path)
    if not resolved.exists():
        return False, f"File does not exist: {resolved.name}"
    if not resolved.is_file():
        return False, "Path is not a file"

    ext = resolved.suffix.lower()
    if ext not in _VALID_EXTENSIONS:
        return False, f"Unsupported format '{ext}'. Use JPG, PNG, or WEBP."

    if not _PIL_AVAILABLE:
        return True, ""

    try:
        with Image.open(resolved) as img:
            img.load()
    except (UnidentifiedImageError, Exception):
        return False, "File is not a valid image or is corrupted"

    return True, ""
