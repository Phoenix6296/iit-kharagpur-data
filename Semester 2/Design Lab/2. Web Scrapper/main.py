import requests
import sqlite3
import os
from dotenv import load_dotenv
from datetime import datetime
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

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

class AsteroidDataVisualizer:
    #Visulaize the top 5 fastest asteroids
    def visualize_top_5_fastest_asteroids(self, data):
        df = pd.DataFrame(data, columns=["Name", "Velocity", "Hazardous"])
        sns.barplot(x="Velocity", y="Name", hue="Hazardous", data=df)
        plt.title("Top 5 Fastest Asteroids")
        plt.xlabel("Velocity (km/h)")
        plt.ylabel("Name")
        plt.savefig("top_5_fastest_asteroids.png")

    #Visualize the hazardous asteroids
    def visualize_hazardous_asteroids(self, data):
        df = pd.DataFrame(data, columns=["Name", "Min Diameter", "Max Diameter", "Velocity"])
        sns.scatterplot(x="Min Diameter", y="Max Diameter", hue="Velocity", data=df)
        plt.title("Hazardous Asteroids")
        plt.xlabel("Min Diameter (km)")
        plt.ylabel("Max Diameter (km)")
        plt.savefig("hazardous_asteroids.png")

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
        
        #Print the headings
        print("Top 5 Fastest Asteroids")
        print("Name\tVelocity\tHazardous")
        for asteroid in asteroid_data.display_top_5_fastest_asteroids():
            print(f"{asteroid[0]}\t{asteroid[1]}\t{asteroid[2]}")
        
        print("\nHazardous Asteroids")
        print("Name\tMin Diameter\tMax Diameter\tVelocity")
        for asteroid in asteroid_data.display_hazardous_asteroids():
            print(f"{asteroid[0]}\t{asteroid[1]}\t{asteroid[2]}\t{asteroid[3]}")

        # Visualize the data
        visualizer = AsteroidDataVisualizer()
        visualizer.visualize_top_5_fastest_asteroids(asteroid_data.display_top_5_fastest_asteroids())
        visualizer.visualize_hazardous_asteroids(asteroid_data.display_hazardous_asteroids())
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
    except sqlite3.Error as se:
        print(f"SQLite Error: {se}")
    except ValueError as ve:
        print(f"Error: {ve}")
    except Exception as e:
        print(f"An error occurred: {e}")