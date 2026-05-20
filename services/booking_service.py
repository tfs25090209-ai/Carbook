"""Booking service for car reservations."""

from datetime import date, datetime, time
from decimal import Decimal
from typing import Dict, List, Optional, Tuple

from database import db
from services.car_service import CarService
from utils.auth import Session


class BookingService:
    """Service layer for booking validation and persistence."""

    ACTIVE_STATUSES = ("pending", "confirmed", "active")

    @classmethod
    def calculate_total(
        cls,
        car_id: int,
        start_date_text: str,
        end_date_text: str
    ) -> Tuple[bool, str, Optional[Dict]]:
        """Calculate booking days and total price."""
        valid, message, parsed = cls._validate_dates(start_date_text, end_date_text)
        if not valid:
            return False, message, None

        car = CarService.get_by_id(car_id)
        if not car:
            return False, "Selected car was not found", None

        total_days = (parsed["end_date"] - parsed["start_date"]).days + 1
        daily_rate = Decimal(str(car["daily_rate"]))
        total_price = daily_rate * total_days

        return True, "", {
            "car": car,
            "start_date": parsed["start_date"],
            "end_date": parsed["end_date"],
            "pickup_datetime": datetime.combine(parsed["start_date"], time.min),
            "dropoff_datetime": datetime.combine(parsed["end_date"], time.max.replace(microsecond=0)),
            "total_days": total_days,
            "total_price": total_price,
        }

    @classmethod
    def create_booking(
        cls,
        user_id: int,
        car_id: int,
        start_date_text: str,
        end_date_text: str,
        pickup_location: str = "Main Branch",
        dropoff_location: str = "Main Branch"
    ) -> Tuple[bool, str, Optional[Dict]]:
        """Create a booking if the car is available for the date range."""
        if not user_id:
            return False, "Please log in before booking a car", None

        pickup_location = pickup_location.strip() or "Main Branch"
        dropoff_location = dropoff_location.strip() or "Main Branch"

        valid, message, quote = cls.calculate_total(car_id, start_date_text, end_date_text)
        if not valid:
            return False, message, None

        car = quote["car"]
        if car["status"] in ("maintenance", "unavailable"):
            return False, "This car is currently unavailable", None

        if cls.has_conflicting_booking(car_id, quote["pickup_datetime"], quote["dropoff_datetime"]):
            return False, "This car is already booked for those dates", None

        booking_id = db.insert("bookings", {
            "user_id": user_id,
            "car_id": car_id,
            "pickup_location": pickup_location,
            "dropoff_location": dropoff_location,
            "pickup_date": quote["pickup_datetime"],
            "dropoff_date": quote["dropoff_datetime"],
            "total_days": quote["total_days"],
            "total_price": quote["total_price"],
            "status": "confirmed",
            "payment_status": "pending",
            "notes": None,
        })

        if not booking_id:
            return False, "Failed to create booking", None

        cls.refresh_car_availability(car_id)
        booking = cls.get_by_id(booking_id)
        return True, "Booking confirmed", booking

    @classmethod
    def has_conflicting_booking(
        cls,
        car_id: int,
        pickup_datetime: datetime,
        dropoff_datetime: datetime
    ) -> bool:
        """Return whether a car is booked for any overlapping date range."""
        placeholders = ", ".join(["%s"] * len(cls.ACTIVE_STATUSES))
        query = (
            "SELECT id FROM bookings "
            "WHERE car_id = %s "
            f"AND status IN ({placeholders}) "
            "AND pickup_date <= %s "
            "AND dropoff_date >= %s "
            "LIMIT 1"
        )
        params = (car_id, *cls.ACTIVE_STATUSES, dropoff_datetime, pickup_datetime)
        return db.fetch_one(query, params) is not None

    @classmethod
    def refresh_car_availability(cls, car_id: int) -> None:
        """Set a car to rented only when it has an active booking today."""
        now = datetime.now()
        placeholders = ", ".join(["%s"] * len(cls.ACTIVE_STATUSES))
        active = db.fetch_one(
            "SELECT id FROM bookings "
            "WHERE car_id = %s "
            f"AND status IN ({placeholders}) "
            "AND pickup_date <= %s "
            "AND dropoff_date >= %s "
            "LIMIT 1",
            (car_id, *cls.ACTIVE_STATUSES, now, now)
        )

        car = CarService.get_by_id(car_id)
        if not car or car["status"] in ("maintenance", "unavailable"):
            return

        status = "rented" if active else "available"
        db.update("cars", {"status": status}, "id = %s", (car_id,))

    @staticmethod
    def get_by_id(booking_id: int) -> Optional[Dict]:
        """Return booking details by ID."""
        return db.fetch_one(
            "SELECT b.*, c.brand, c.model, c.license_plate, c.daily_rate "
            "FROM bookings b "
            "JOIN cars c ON c.id = b.car_id "
            "WHERE b.id = %s",
            (booking_id,)
        )

    @classmethod
    def cancel_booking(cls, booking_id: int, user_id: int) -> Tuple[bool, str]:
        """Cancel a booking.
        
        Customers can only cancel their own bookings.
        Admins can cancel any booking.
        """
        booking = db.fetch_one(
            "SELECT * FROM bookings WHERE id = %s",
            (booking_id,)
        )

        if not booking:
            return False, "Booking was not found"

        # Ensure customers can only cancel their own bookings
        if not Session.is_admin() and booking["user_id"] != user_id:
            return False, "You can only cancel your own bookings"

        if booking["status"] not in cls.ACTIVE_STATUSES:
            return False, "Only active bookings can be cancelled"

        if booking["dropoff_date"].date() < date.today():
            return False, "Past bookings cannot be cancelled"

        updated = db.update(
            "bookings",
            {"status": "cancelled"},
            "id = %s",
            (booking_id,)
        )

        if not updated:
            return False, "Failed to cancel booking"

        cls.refresh_car_availability(booking["car_id"])
        return True, "Booking cancelled"

    @classmethod
    def cancel(cls, booking_id: int) -> Tuple[bool, str]:
        """Cancel a booking using current user from session."""
        user_id = Session.get_user_id()
        return cls.cancel_booking(booking_id, user_id)

    @classmethod
    def extend(cls, booking_id: int, new_end_date: str) -> Tuple[bool, str]:
        """Extend a booking to a new end date."""
        user_id = Session.get_user_id()
        if not user_id:
            return False, "Please log in to extend a booking"

        booking = db.fetch_one(
            "SELECT * FROM bookings WHERE id = %s",
            (booking_id,)
        )

        if not booking:
            return False, "Booking was not found"

        # Verify ownership for non-admin
        if not Session.is_admin() and booking["user_id"] != user_id:
            return False, "You can only extend your own bookings"

        if booking["status"] not in cls.ACTIVE_STATUSES:
            return False, "Only active bookings can be extended"

        # Validate new end date
        valid, message, parsed = cls._validate_dates(
            booking["pickup_date"].strftime("%Y-%m-%d"),
            new_end_date
        )
        if not valid:
            return False, message

        new_end = parsed["end_date"]
        if new_end <= booking["dropoff_date"].date():
            return False, "New end date must be after current end date"

        # Calculate additional cost
        extra_days = (new_end - booking["dropoff_date"].date()).days
        car = CarService.get_by_id(booking["car_id"])
        if not car:
            return False, "Car not found"

        additional_cost = Decimal(str(car["daily_rate"])) * extra_days

        # Update booking
        updated = db.update(
            "bookings",
            {
                "dropoff_date": datetime.combine(new_end, time.max.replace(microsecond=0)),
                "total_days": booking["total_days"] + extra_days,
                "total_price": booking["total_price"] + additional_cost,
            },
            "id = %s",
            (booking_id,)
        )

        if not updated:
            return False, "Failed to extend booking"

        cls.refresh_car_availability(booking["car_id"])
        return True, f"Booking extended by {extra_days} day(s)"

    @staticmethod
    def get_user_bookings(user_id: int) -> List[Dict]:
        """Return all bookings for a user."""
        if not user_id:
            return []

        return db.fetch_all(
            "SELECT b.*, c.brand, c.model, c.license_plate, c.image_url, c.daily_rate "
            ", c.year, c.color, c.category, c.transmission, c.fuel_type, c.seats "
            "FROM bookings b "
            "JOIN cars c ON c.id = b.car_id "
            "WHERE b.user_id = %s "
            "ORDER BY b.pickup_date DESC, b.id DESC",
            (user_id,)
        )

    @staticmethod
    def _validate_dates(start_date_text: str, end_date_text: str) -> Tuple[bool, str, Dict]:
        try:
            start_date = date.fromisoformat(start_date_text.strip())
            end_date = date.fromisoformat(end_date_text.strip())
        except ValueError:
            return False, "Use dates in YYYY-MM-DD format", {}

        today = date.today()
        if start_date < today:
            return False, "Start date cannot be in the past", {}

        if end_date < start_date:
            return False, "End date must be on or after the start date", {}

        return True, "", {"start_date": start_date, "end_date": end_date}
