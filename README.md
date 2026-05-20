# LuxuryDrive Car Booking System

A modern desktop luxury car rental management app built with Python, CustomTkinter, and MySQL.

## Features

- User registration and login with salted password hashing
- Session handling and logout confirmation
- Dashboard with navigation sidebar
- Car inventory management with add, edit, delete, search, filters, availability, and image upload
- Booking flow with date validation, automatic price calculation, confirmation dialog, and overlap prevention
- My Bookings page with current bookings, booking history, status display, car details, and cancellation
- Dark modern CustomTkinter UI with shared theme constants
- Seeded LuxuryDrive demo accounts, luxury fleet, and sample bookings on launch

## Demo Login

Admin:

```text
Email: admin@luxurydrive.com
Password: admin123
```

Customer:

```text
Email: user@luxurydrive.com
Password: user123
```

## Project Structure

```text
Carbook/
  app.py                     # Main CustomTkinter application shell
  main.py                    # App entry point
  database/
    db.py                    # MySQL connection, schema creation, query helpers
  services/
    auth_service.py          # Registration and login business logic
    car_service.py           # Car CRUD, filters, image copy helper
    booking_service.py       # Booking validation, pricing, conflict checks, cancellation
  ui/
    pages/                   # Landing, auth, dashboard, cars, bookings, profile placeholder
    widgets/                 # Shared UI widgets
  utils/
    auth.py                  # Password hashing, validation, session state
  theme/
    colors.py                # Shared palette and spacing constants
  assets/car_images/         # Uploaded car images
```

## Requirements

- Python 3.10+
- MySQL Server running locally or remotely
- A MySQL user with permission to create the configured database and tables

Python dependencies are listed in `requirements.txt`.

## Setup

1. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create your environment file:

```bash
cp .env.example .env
```

4. Edit `.env` with your MySQL settings:

```text
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=car_booking
```

5. Start MySQL, then run the app:

```bash
python main.py
```

On startup, the app connects to MySQL, creates the configured database if needed, creates the `users`, `cars`, and `bookings` tables if they do not already exist, then seeds demo data.

## Database Tables

- `users`: authentication profile, password hash, role, active flag
- `cars`: inventory details, status, daily rate, uploaded image path
- `bookings`: user/car reservation dates, total days, total price, booking/payment status

## Demo Data

The startup seed creates:

- 1 admin account and 1 customer account
- 12 premium vehicles from Rolls-Royce, Lamborghini, Ferrari, Porsche, BMW, Mercedes-Benz, Audi, and Bentley
- realistic daily pricing from ₹28,000/day to ₹75,000/day
- active, completed, and cancelled sample bookings for the customer account

## Notes

- Dates in the booking form use `YYYY-MM-DD`.
- Booking dates are inclusive: a same-day booking counts as 1 day.
- The app prevents overlapping active bookings for the same car.
- Car status is set to `rented` only when an active booking includes today; future bookings keep the car available for non-overlapping ranges.
