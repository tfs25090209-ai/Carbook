"""Car management service for database CRUD operations."""

from pathlib import Path
import shutil
from typing import Dict, List, Optional, Tuple

from database import db
from utils.auth import Session
from utils.image_loader import validate_image_file


class CarService:
    """Service layer for car inventory management."""

    CATEGORIES = ("all", "sedan", "suv", "truck", "van", "sports")
    STATUSES = ("all", "available", "rented", "maintenance", "unavailable")
    TRANSMISSIONS = ("automatic", "manual")
    FUEL_TYPES = ("petrol", "diesel", "electric", "hybrid")

    IMAGE_DIR = Path(__file__).parent.parent / "assets" / "car_images"

    @classmethod
    def get_all(
        cls,
        search: str = "",
        category: str = "all",
        status: str = "all"
    ) -> List[Dict]:
        """Return cars filtered by search text, category, and status."""
        query = "SELECT * FROM cars"
        clauses = []
        params = []

        if search:
            like_search = f"%{search}%"
            clauses.append(
                "(brand LIKE %s OR model LIKE %s OR license_plate LIKE %s OR color LIKE %s)"
            )
            params.extend([like_search, like_search, like_search, like_search])

        if category and category != "all":
            clauses.append("category = %s")
            params.append(category)

        if status and status != "all":
            clauses.append("status = %s")
            params.append(status)

        if clauses:
            query += " WHERE " + " AND ".join(clauses)

        query += " ORDER BY created_at DESC, id DESC"
        return db.fetch_all(query, tuple(params))

    @staticmethod
    def get_by_id(car_id: int) -> Optional[Dict]:
        """Return a car by ID."""
        return db.fetch_one("SELECT * FROM cars WHERE id = %s", (car_id,))

    @classmethod
    def create(cls, data: Dict) -> Tuple[bool, str]:
        """Create a new car (admin only)."""
        # Check admin access
        if not Session.is_admin():
            return False, "Admin access required to add cars"

        valid, message, cleaned = cls._validate(data)
        if not valid:
            return False, message

        if cls._license_plate_exists(cleaned["license_plate"]):
            return False, "License plate already exists"

        car_id = db.insert("cars", cleaned)
        if car_id:
            return True, "Car added successfully"
        return False, "Failed to add car"

    @classmethod
    def update(cls, car_id: int, data: Dict) -> Tuple[bool, str]:
        """Update an existing car (admin only)."""
        # Check admin access
        if not Session.is_admin():
            return False, "Admin access required to edit cars"

        valid, message, cleaned = cls._validate(data)
        if not valid:
            return False, message

        if cls._license_plate_exists(cleaned["license_plate"], exclude_id=car_id):
            return False, "License plate already exists"

        if db.update("cars", cleaned, "id = %s", (car_id,)):
            return True, "Car updated successfully"
        return False, "Failed to update car"

    @staticmethod
    def delete(car_id: int) -> Tuple[bool, str]:
        """Delete a car (admin only)."""
        # Check admin access
        if not Session.is_admin():
            return False, "Admin access required to delete cars"

        if db.delete("cars", "id = %s", (car_id,)):
            return True, "Car deleted successfully"
        return False, "Failed to delete car"

    @classmethod
    def copy_image(cls, source_path: str) -> Optional[str]:
        """Copy an uploaded image into the app assets folder.

        Validates the file type and readability before copying.
        Returns the destination path on success, None on failure.
        """
        if not source_path:
            return None

        is_valid, _message = validate_image_file(source_path)
        if not is_valid:
            return None

        source = Path(source_path)
        cls.IMAGE_DIR.mkdir(parents=True, exist_ok=True)
        safe_stem = "".join(ch for ch in source.stem if ch.isalnum() or ch in ("-", "_"))
        filename = f"{safe_stem or 'car'}_{source.stat().st_mtime_ns}{source.suffix.lower()}"
        destination = cls.IMAGE_DIR / filename
        shutil.copy2(source, destination)
        return str(destination)

    @staticmethod
    def _license_plate_exists(license_plate: str, exclude_id: Optional[int] = None) -> bool:
        query = "SELECT id FROM cars WHERE license_plate = %s"
        params = [license_plate]

        if exclude_id is not None:
            query += " AND id <> %s"
            params.append(exclude_id)

        return db.fetch_one(query, tuple(params)) is not None

    @classmethod
    def _validate(cls, data: Dict) -> Tuple[bool, str, Dict]:
        required_fields = ("brand", "model", "year", "license_plate", "category", "daily_rate")
        cleaned = {}

        for field in required_fields:
            value = str(data.get(field, "")).strip()
            if not value:
                return False, f"{field.replace('_', ' ').title()} is required", {}
            cleaned[field] = value

        try:
            cleaned["year"] = int(cleaned["year"])
        except ValueError:
            return False, "Year must be a number", {}

        if cleaned["year"] < 1950 or cleaned["year"] > 2100:
            return False, "Year must be between 1950 and 2100", {}

        try:
            cleaned["daily_rate"] = float(cleaned["daily_rate"])
        except ValueError:
            return False, "Daily rate must be a number", {}

        if cleaned["daily_rate"] <= 0:
            return False, "Daily rate must be greater than 0", {}

        try:
            seats = int(str(data.get("seats", "5")).strip() or "5")
        except ValueError:
            return False, "Seats must be a number", {}

        if seats <= 0:
            return False, "Seats must be greater than 0", {}

        category = cleaned["category"].lower()
        if category not in cls.CATEGORIES[1:]:
            return False, "Invalid category", {}

        status = str(data.get("status", "available")).strip().lower()
        if status not in cls.STATUSES[1:]:
            return False, "Invalid availability status", {}

        transmission = str(data.get("transmission", "automatic")).strip().lower()
        if transmission not in cls.TRANSMISSIONS:
            return False, "Invalid transmission", {}

        fuel_type = str(data.get("fuel_type", "petrol")).strip().lower()
        if fuel_type not in cls.FUEL_TYPES:
            return False, "Invalid fuel type", {}

        cleaned.update({
            "license_plate": cleaned["license_plate"].upper(),
            "category": category,
            "status": status,
            "transmission": transmission,
            "fuel_type": fuel_type,
            "color": str(data.get("color", "")).strip() or None,
            "seats": seats,
            "description": str(data.get("description", "")).strip() or None,
            "image_url": str(data.get("image_url", "")).strip() or None,
        })

        return True, "", cleaned
