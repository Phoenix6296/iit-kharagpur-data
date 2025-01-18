import requests
import sqlite3
import os
from dotenv import load_dotenv
from datetime import datetime

# Load the .env file
load_dotenv()

# Access the API key and other configurations from the environment variables
API_KEY = os.getenv("API_KEY")
API_URL = os.getenv("API_URL")
DB_NAME = os.getenv("DB_NAME")

if not API_KEY or not API_URL:
    raise EnvironmentError("API_KEY, API_URL, or DB_NAME not found in environment variables.")

class AsteroidData:
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        self.conn = sqlite3.connect(DB_NAME)
        self.c = self.conn.cursor()

    def __del__(self):
        self.conn.close()

    def fetch_asteroid_data(self):
        params = {"start_date": self.start_date, "end_date": self.end_date, "api_key": API_KEY}
        response = requests.get(API_URL, params=params)
        response.raise_for_status()
        return response.json()

    def create_table(self):
        self.c.execute("""
            CREATE TABLE IF NOT EXISTS asteroid_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                min_diameter REAL,
                max_diameter REAL,
                hazardous INTEGER,
                close_approach_date TEXT,
                velocity REAL
            )
        """)
        self.conn.commit()

    def store_data_in_db(self, data):
        for date, asteroids in data["near_earth_objects"].items():
            for asteroid in asteroids:
                name = asteroid["name"]
                min_diameter = asteroid["estimated_diameter"]["kilometers"]["estimated_diameter_min"]
                max_diameter = asteroid["estimated_diameter"]["kilometers"]["estimated_diameter_max"]
                hazardous = 1 if asteroid["is_potentially_hazardous_asteroid"] else 0
                close_approach_date = asteroid["close_approach_data"][0]["close_approach_date"]
                velocity = asteroid["close_approach_data"][0]["relative_velocity"]["kilometers_per_hour"]
                self.c.execute("""
                    INSERT INTO asteroid_data (name, min_diameter, max_diameter, hazardous, close_approach_date, velocity)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (name, min_diameter, max_diameter, hazardous, close_approach_date, velocity))
        self.conn.commit()

    def display_top_5_fastest_asteroids(self):
        self.c.execute("SELECT name, velocity, hazardous FROM asteroid_data ORDER BY velocity DESC LIMIT 5")
        return self.c.fetchall()

    def display_hazardous_asteroids(self):
        self.c.execute("SELECT name, min_diameter, max_diameter, velocity FROM asteroid_data WHERE hazardous = 1")
        return self.c.fetchall()

# Utility functions
def validate_date(date_str):
    """Validate the format of a date string."""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def validate_date_range(start_date, end_date):
    """Validate that the start_date comes before the end_date."""
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    if start > end:
        raise ValueError("Start date cannot be after the end date.")

if __name__ == "__main__":
    start_date = input("Enter the start date (YYYY-MM-DD): ")
    end_date = input("Enter the end date (YYYY-MM-DD): ")

    try:
        # Validate date formats
        if not (validate_date(start_date) and validate_date(end_date)):
            raise ValueError("Invalid date format. Please use YYYY-MM-DD.")

        # Validate date range
        validate_date_range(start_date, end_date)

        # Initialize and process asteroid data
        asteroid_data = AsteroidData(start_date, end_date)
        data = asteroid_data.fetch_asteroid_data()
        asteroid_data.create_table()
        asteroid_data.store_data_in_db(data)
        
        print("\nTop 5 Fastest Asteroids:")
        for asteroid in asteroid_data.display_top_5_fastest_asteroids():
            print(f"Name: {asteroid[0]}, Velocity: {float(asteroid[1]):.2f} km/h, Hazardous: {'Yes' if asteroid[2] else 'No'}")

        print("\nHazardous Asteroids:")
        for asteroid in asteroid_data.display_hazardous_asteroids():
            print(f"Name: {asteroid[0]}, Min Diameter: {asteroid[1]:.2f} km, Max Diameter: {asteroid[2]:.2f} km, Velocity: {float(asteroid[3]):.2f} km/h")

    except ValueError as ve:
        print(f"Value Error: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
