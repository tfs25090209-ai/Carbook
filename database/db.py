"""Database module for Car Booking System."""

import os
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# Load environment variables from project root using pathlib
# This ensures .env is found regardless of current working directory
ENV_PATH = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=ENV_PATH)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Database:
    """Database manager for MySQL operations."""

    _instance = None
    _allowed_tables = {"users", "cars", "bookings"}
    _identifier_pattern = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

    def __new__(cls):
        """Singleton pattern to maintain one DB connection."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._connection = None
            cls._instance._config = None
        return cls._instance

    def connect(self) -> bool:
        """Establish connection to MySQL server."""

        try:
            self._config = {
                "host": os.getenv("DB_HOST", "localhost"),
                "port": int(os.getenv("DB_PORT", 3306)),
                "user": os.getenv("DB_USER", "root"),
                "password": os.getenv("DB_PASSWORD", ""),
            }

            database = self._safe_identifier(os.getenv("DB_NAME", "car_booking"))

            # Connect without selecting database first
            self._connection = mysql.connector.connect(**self._config)

            # Store DB name for later use
            self._config["database"] = database

            logger.info(
                f"Connected to MySQL server at "
                f"{self._config['host']}:{self._config['port']}"
            )

            return True

        except (Error, ValueError) as e:
            logger.error(f"Failed to connect to MySQL: {e}")
            return False

    def reconnect_if_needed(self) -> None:
        """Reconnect if database connection is lost."""

        if not self.is_connected:
            logger.warning("Database connection lost. Reconnecting...")
            if self.connect():
                self.initialize_database()

    def initialize_database(self) -> bool:
        """Create database and required tables."""

        try:
            self.reconnect_if_needed()

            cursor = self._connection.cursor()

            db_name = self._safe_identifier(self._config["database"])

            # Create database
            cursor.execute(
                f"""
                CREATE DATABASE IF NOT EXISTS `{db_name}`
                CHARACTER SET utf8mb4
                COLLATE utf8mb4_unicode_ci
                """
            )

            # Select database
            cursor.execute(f"USE `{db_name}`")

            # Reconnect with database selected
            self._connection.database = db_name

            # Create tables
            self._create_tables(cursor)

            self._connection.commit()
            cursor.close()

            logger.info("Database initialized successfully")

            return True

        except (Error, ValueError) as e:
            logger.error(f"Database initialization failed: {e}")
            return False

    def _create_tables(self, cursor) -> None:
        """Create all required tables."""

        # USERS TABLE
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,

                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,

                full_name VARCHAR(100) NOT NULL,
                phone VARCHAR(20),

                role ENUM('admin', 'customer')
                DEFAULT 'customer',

                is_active BOOLEAN DEFAULT TRUE,

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ON UPDATE CURRENT_TIMESTAMP,

                INDEX idx_email (email),
                INDEX idx_username (username),
                INDEX idx_role (role)

            ) ENGINE=InnoDB
            DEFAULT CHARSET=utf8mb4
            COLLATE=utf8mb4_unicode_ci
        """)

        # CARS TABLE
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cars (
                id INT AUTO_INCREMENT PRIMARY KEY,

                brand VARCHAR(50) NOT NULL,
                model VARCHAR(50) NOT NULL,
                year INT NOT NULL,

                license_plate VARCHAR(20)
                UNIQUE NOT NULL,

                color VARCHAR(30),

                category ENUM(
                    'sedan',
                    'suv',
                    'truck',
                    'van',
                    'sports'
                ) NOT NULL,

                transmission ENUM(
                    'automatic',
                    'manual'
                ) DEFAULT 'automatic',

                fuel_type ENUM(
                    'petrol',
                    'diesel',
                    'electric',
                    'hybrid'
                ) DEFAULT 'petrol',

                daily_rate DECIMAL(10,2) NOT NULL,

                seats INT DEFAULT 5,

                status ENUM(
                    'available',
                    'rented',
                    'maintenance',
                    'unavailable'
                ) DEFAULT 'available',

                description TEXT,
                image_url VARCHAR(255),

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ON UPDATE CURRENT_TIMESTAMP,

                INDEX idx_brand_model (brand, model),
                INDEX idx_status (status),
                INDEX idx_category (category),
                INDEX idx_license_plate (license_plate)

            ) ENGINE=InnoDB
            DEFAULT CHARSET=utf8mb4
            COLLATE=utf8mb4_unicode_ci
        """)

        # BOOKINGS TABLE
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                id INT AUTO_INCREMENT PRIMARY KEY,

                user_id INT NOT NULL,
                car_id INT NOT NULL,

                pickup_location VARCHAR(100) NOT NULL,
                dropoff_location VARCHAR(100) NOT NULL,

                pickup_date DATETIME NOT NULL,
                dropoff_date DATETIME NOT NULL,

                total_days INT NOT NULL,
                total_price DECIMAL(10,2) NOT NULL,

                status ENUM(
                    'pending',
                    'confirmed',
                    'active',
                    'completed',
                    'cancelled'
                ) DEFAULT 'pending',

                payment_status ENUM(
                    'pending',
                    'paid',
                    'refunded'
                ) DEFAULT 'pending',

                payment_method VARCHAR(50),

                notes TEXT,

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ON UPDATE CURRENT_TIMESTAMP,

                CONSTRAINT fk_booking_user
                FOREIGN KEY (user_id)
                REFERENCES users(id)
                ON DELETE RESTRICT
                ON UPDATE CASCADE,

                CONSTRAINT fk_booking_car
                FOREIGN KEY (car_id)
                REFERENCES cars(id)
                ON DELETE RESTRICT
                ON UPDATE CASCADE,

                INDEX idx_user_id (user_id),
                INDEX idx_car_id (car_id),
                INDEX idx_status (status),
                INDEX idx_pickup_date (pickup_date),
                INDEX idx_dropoff_date (dropoff_date)

            ) ENGINE=InnoDB
            DEFAULT CHARSET=utf8mb4
            COLLATE=utf8mb4_unicode_ci
        """)

    def execute_query(
        self,
        query: str,
        params: Optional[Tuple] = None
    ) -> Optional[Any]:
        """Execute INSERT, UPDATE, DELETE queries."""

        cursor = None

        try:
            self.reconnect_if_needed()

            cursor = self._connection.cursor(dictionary=True)

            cursor.execute(query, params or ())

            self._connection.commit()

            return cursor.lastrowid if cursor.lastrowid else True

        except Error as e:
            logger.error(f"Query execution failed: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params}")

            if self._connection:
                self._connection.rollback()

            return None

        finally:
            if cursor:
                cursor.close()

    def fetch_one(
        self,
        query: str,
        params: Optional[Tuple] = None
    ) -> Optional[Dict[str, Any]]:
        """Fetch a single row."""

        cursor = None

        try:
            self.reconnect_if_needed()

            cursor = self._connection.cursor(dictionary=True)

            cursor.execute(query, params or ())

            return cursor.fetchone()

        except Error as e:
            logger.error(f"Fetch one failed: {e}")
            return None

        finally:
            if cursor:
                cursor.close()

    def fetch_all(
        self,
        query: str,
        params: Optional[Tuple] = None
    ) -> List[Dict[str, Any]]:
        """Fetch all rows."""

        cursor = None

        try:
            self.reconnect_if_needed()

            cursor = self._connection.cursor(dictionary=True)

            cursor.execute(query, params or ())

            return cursor.fetchall()

        except Error as e:
            logger.error(f"Fetch all failed: {e}")
            return []

        finally:
            if cursor:
                cursor.close()

    def insert(
        self,
        table: str,
        data: Dict[str, Any]
    ) -> Optional[int]:
        """Insert a row into table."""
        table = self._safe_table(table)

        columns = ", ".join([f"`{self._safe_identifier(column)}`" for column in data.keys()])
        placeholders = ", ".join(["%s"] * len(data))

        query = (
            f"INSERT INTO `{table}` "
            f"({columns}) "
            f"VALUES ({placeholders})"
        )

        return self.execute_query(
            query,
            tuple(data.values())
        )

    def update(
        self,
        table: str,
        data: Dict[str, Any],
        where: str,
        params: Optional[Tuple] = None
    ) -> bool:
        """Update rows in table."""
        table = self._safe_table(table)

        set_clause = ", ".join(
            [f"`{self._safe_identifier(key)}` = %s" for key in data.keys()]
        )

        query = (
            f"UPDATE `{table}` "
            f"SET {set_clause} "
            f"WHERE {where}"
        )

        all_params = tuple(data.values()) + (params or ())

        result = self.execute_query(query, all_params)

        return result is not None

    def delete(
        self,
        table: str,
        where: str,
        params: Optional[Tuple] = None
    ) -> bool:
        """Delete rows from table."""
        table = self._safe_table(table)

        query = f"DELETE FROM `{table}` WHERE {where}"

        result = self.execute_query(query, params)

        return result is not None

    def close(self) -> None:
        """Close database connection."""

        if self._connection and self._connection.is_connected():
            self._connection.close()
            logger.info("Database connection closed")

    @property
    def is_connected(self) -> bool:
        """Check database connection status."""

        return (
            self._connection is not None
            and self._connection.is_connected()
        )

    @classmethod
    def _safe_identifier(cls, identifier: str) -> str:
        """Validate SQL identifiers used outside parameter binding."""
        if not identifier or not cls._identifier_pattern.match(identifier):
            raise ValueError(f"Invalid SQL identifier: {identifier}")
        return identifier

    @classmethod
    def _safe_table(cls, table: str) -> str:
        """Allow helper methods to operate only on known app tables."""
        table = cls._safe_identifier(table)
        if table not in cls._allowed_tables:
            raise ValueError(f"Unsupported table: {table}")
        return table

    # Context manager support
    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# Singleton instance
db = Database()
