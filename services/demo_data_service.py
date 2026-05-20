"""Seed realistic demo data for the luxury car booking experience."""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List

from database import db
from utils.auth import AuthUtils


class DemoDataService:
    """Creates deterministic demo accounts, cars, and bookings."""

    ADMIN_EMAIL = "admin@luxurydrive.com"
    CUSTOMER_EMAIL = "user@luxurydrive.com"

    DEMO_USERS = [
        {
            "username": "luxury_admin",
            "email": ADMIN_EMAIL,
            "password": "admin123",
            "full_name": "LuxuryDrive Admin",
            "phone": "+911111111111",
            "role": "admin",
        },
        {
            "username": "luxury_user",
            "email": CUSTOMER_EMAIL,
            "password": "user123",
            "full_name": "Aarav Kapoor",
            "phone": "+919999999999",
            "role": "customer",
        },
    ]

    DEMO_CARS = [
        ("Rolls-Royce", "Ghost Extended", 2024, "LD-RR-001", "Arctic White", "sedan", "petrol", "automatic", 5, 75000, "available"),
        ("Rolls-Royce", "Cullinan", 2024, "LD-RR-002", "Black Diamond", "suv", "petrol", "automatic", 5, 72000, "available"),
        ("Lamborghini", "Huracan Evo", 2023, "LD-LAM-01", "Verde Mantis", "sports", "petrol", "automatic", 2, 68000, "available"),
        ("Lamborghini", "Urus Performante", 2024, "LD-LAM-02", "Nero Noctis", "suv", "petrol", "automatic", 5, 62000, "available"),
        ("Ferrari", "Roma", 2023, "LD-FER-01", "Rosso Corsa", "sports", "petrol", "automatic", 4, 66000, "available"),
        ("Ferrari", "Portofino M", 2022, "LD-FER-02", "Blu Tour De France", "sports", "petrol", "automatic", 4, 64000, "available"),
        ("Porsche", "911 Carrera S", 2024, "LD-POR-01", "Guards Red", "sports", "petrol", "automatic", 4, 42000, "available"),
        ("Porsche", "Cayenne Turbo GT", 2024, "LD-POR-02", "Crayon Grey", "suv", "petrol", "automatic", 5, 39000, "available"),
        ("BMW", "7 Series M Sport", 2024, "LD-BMW-01", "Carbon Black", "sedan", "hybrid", "automatic", 5, 28000, "available"),
        ("Mercedes-Benz", "S-Class Maybach", 2024, "LD-MBZ-01", "Obsidian Black", "sedan", "petrol", "automatic", 5, 45000, "available"),
        ("Audi", "RS e-tron GT", 2024, "LD-AUD-01", "Daytona Grey", "sports", "electric", "automatic", 4, 36000, "available"),
        ("Bentley", "Bentayga Azure", 2024, "LD-BEN-01", "Sequin Blue", "suv", "petrol", "automatic", 5, 52000, "available"),
    ]

    @classmethod
    def seed(cls) -> None:
        """Seed demo data idempotently."""
        users = cls._seed_users()
        cars = cls._seed_cars()
        cls._seed_bookings(users["customer"]["id"], cars)

    @classmethod
    def _seed_users(cls) -> Dict[str, Dict]:
        seeded = {}
        for user in cls.DEMO_USERS:
            existing = db.fetch_one("SELECT * FROM users WHERE email = %s", (user["email"],))
            data = {
                "username": user["username"],
                "email": user["email"],
                "password_hash": AuthUtils.hash_password(user["password"]),
                "full_name": user["full_name"],
                "phone": user["phone"],
                "role": user["role"],
                "is_active": True,
            }

            if existing:
                db.update("users", data, "id = %s", (existing["id"],))
                seeded_user = db.fetch_one("SELECT * FROM users WHERE id = %s", (existing["id"],))
            else:
                user_id = db.insert("users", data)
                seeded_user = db.fetch_one("SELECT * FROM users WHERE id = %s", (user_id,))

            key = "admin" if user["role"] == "admin" else "customer"
            seeded[key] = seeded_user

        return seeded

    @classmethod
    def _seed_cars(cls) -> Dict[str, Dict]:
        seeded = {}
        for brand, model, year, plate, color, category, fuel, transmission, seats, rate, status in cls.DEMO_CARS:
            data = {
                "brand": brand,
                "model": model,
                "year": year,
                "license_plate": plate,
                "color": color,
                "category": category,
                "transmission": transmission,
                "fuel_type": fuel,
                "daily_rate": Decimal(rate),
                "seats": seats,
                "status": status,
                "description": f"Premium {brand} {model} prepared for LuxuryDrive demo rentals.",
                "image_url": None,
            }
            existing = db.fetch_one("SELECT id FROM cars WHERE license_plate = %s", (plate,))
            if existing:
                db.update("cars", data, "id = %s", (existing["id"],))
                car = db.fetch_one("SELECT * FROM cars WHERE id = %s", (existing["id"],))
            else:
                car_id = db.insert("cars", data)
                car = db.fetch_one("SELECT * FROM cars WHERE id = %s", (car_id,))

            seeded[plate] = car

        return seeded

    @classmethod
    def _seed_bookings(cls, customer_id: int, cars: Dict[str, Dict]) -> None:
        db.delete("bookings", "user_id = %s AND notes LIKE %s", (customer_id, "Demo seed:%"))

        now = datetime.now()
        bookings = [
            {
                "car": cars["LD-RR-001"],
                "pickup_date": now - timedelta(days=1),
                "dropoff_date": now + timedelta(days=2),
                "status": "active",
                "payment_status": "paid",
                "notes": "Demo seed: active booking",
            },
            {
                "car": cars["LD-MBZ-01"],
                "pickup_date": now - timedelta(days=14),
                "dropoff_date": now - timedelta(days=11),
                "status": "completed",
                "payment_status": "paid",
                "notes": "Demo seed: completed booking",
            },
            {
                "car": cars["LD-FER-01"],
                "pickup_date": now + timedelta(days=8),
                "dropoff_date": now + timedelta(days=10),
                "status": "cancelled",
                "payment_status": "refunded",
                "notes": "Demo seed: cancelled booking",
            },
        ]

        for booking in bookings:
            total_days = (booking["dropoff_date"].date() - booking["pickup_date"].date()).days + 1
            total_price = Decimal(str(booking["car"]["daily_rate"])) * total_days
            db.insert("bookings", {
                "user_id": customer_id,
                "car_id": booking["car"]["id"],
                "pickup_location": "LuxuryDrive Mumbai Studio",
                "dropoff_location": "LuxuryDrive Mumbai Studio",
                "pickup_date": booking["pickup_date"],
                "dropoff_date": booking["dropoff_date"],
                "total_days": total_days,
                "total_price": total_price,
                "status": booking["status"],
                "payment_status": booking["payment_status"],
                "notes": booking["notes"],
            })

        db.update("cars", {"status": "rented"}, "id = %s", (cars["LD-RR-001"]["id"],))
