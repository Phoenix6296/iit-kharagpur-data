import requests
import sqlite3
from datetime import datetime
import seaborn as sns
import matplotlib.pyplot as plt

# Constants
API_KEY = "p2AGQTagQsQ97SyE4gAWbmAxe55i2SooapyzixQP"
BASE_URL = "https://api.nasa.gov/neo/rest/v1/feed"
DB_NAME = "asteroid_data.db"

# Function to create SQLite database and table
def create_database():
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS asteroids (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            estimated_diameter_min REAL,
            estimated_diameter_max REAL,
            is_hazardous BOOLEAN,
            close_approach_date TEXT,
            velocity_km_s REAL
        )
    ''')
    connection.commit()
    connection.close()

# Function to fetch data from NeoWs API
def fetch_asteroid_data(start_date, end_date):
    params = {
        "start_date": start_date,
        "end_date": end_date,
        "api_key": API_KEY
    }
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

# Function to parse and store asteroid data in SQLite database
def store_data_in_database(data):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    try:
        near_earth_objects = data.get("near_earth_objects", {})
        for date, asteroids in near_earth_objects.items():
            for asteroid in asteroids:
                name = asteroid.get("name", "Unknown")
                diameter = asteroid.get("estimated_diameter", {}).get("meters", {})
                diameter_min = diameter.get("estimated_diameter_min", 0.0)
                diameter_max = diameter.get("estimated_diameter_max", 0.0)
                is_hazardous = asteroid.get("is_potentially_hazardous_asteroid", False)
                close_approach_data = asteroid.get("close_approach_data", [{}])[0]
                close_approach_date = close_approach_data.get("close_approach_date", "Unknown")
                velocity = close_approach_data.get("relative_velocity", {}).get("kilometers_per_second", 0.0)

                cursor.execute('''
                    INSERT INTO asteroids (
                        name, 
                        estimated_diameter_min, 
                        estimated_diameter_max, 
                        is_hazardous, 
                        close_approach_date, 
                        velocity_km_s
                    ) VALUES (?, ?, ?, ?, ?, ?)
                ''', (name, diameter_min, diameter_max, is_hazardous, close_approach_date, velocity))

        connection.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        connection.close()

# Function to query top 5 fastest asteroids
def query_fastest_asteroids():
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    try:
        cursor.execute('''
            SELECT name, velocity_km_s, is_hazardous 
            FROM asteroids 
            ORDER BY velocity_km_s DESC 
            LIMIT 5
        ''')
        results = cursor.fetchall()
        print("Top 5 Fastest Asteroids:")
        for row in results:
            print(f"Name: {row[0]}, Velocity: {row[1]} km/s, Hazardous: {row[2]}")
        return results
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        connection.close()

# Function to query hazardous asteroids with diameter > 600 meters
def query_hazardous_large_asteroids():
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    try:
        cursor.execute('''
            SELECT name, estimated_diameter_max 
            FROM asteroids 
            WHERE is_hazardous = 1 AND estimated_diameter_max > 600
        ''')
        results = cursor.fetchall()
        print("Hazardous Asteroids with Diameter > 600 meters:")
        for row in results:
            print(f"Name: {row[0]}, Max Diameter: {row[1]} meters")
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        connection.close()

# Function to visualize top 5 fastest asteroids
def visualize_top_fastest_asteroids():
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    try:
        cursor.execute('''
            SELECT name, velocity_km_s 
            FROM asteroids 
            ORDER BY velocity_km_s DESC 
            LIMIT 5
        ''')
        results = cursor.fetchall()
        names = [row[0] for row in results]
        velocities = [row[1] for row in results]

        sns.barplot(x=names, y=velocities)
        plt.title("Top 5 Fastest Asteroids")
        plt.xlabel("Asteroid Name")
        plt.ylabel("Velocity (km/s)")
        plt.grid(True)
        plt.show()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        connection.close()

# Function to visualize velocity vs. diameter with hazardous distinction
def visualize_velocity_vs_diameter():
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    try:
        cursor.execute('''
            SELECT name, velocity_km_s, estimated_diameter_max, is_hazardous 
            FROM asteroids
        ''')
        results = cursor.fetchall()

        velocities = [row[1] for row in results]
        diameters = [row[2] for row in results]
        hazardous = ["Hazardous" if row[3] else "Non-Hazardous" for row in results]
        names = [row[0] for row in results]

        plt.figure(figsize=(10, 6))
        scatter = sns.scatterplot(x=velocities, y=diameters, hue=hazardous, style=hazardous, s=100)

        for i, name in enumerate(names):
            if velocities[i] in sorted(velocities, reverse=True)[:5]:
                plt.annotate(name, (velocities[i], diameters[i]), textcoords="offset points", xytext=(5,5), ha="center")

        plt.title("Velocity vs. Diameter of Asteroids")
        plt.xlabel("Velocity (km/s)")
        plt.ylabel("Max Diameter (meters)")
        plt.legend(title="Hazardous Status")
        plt.grid(True)
        plt.show()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        connection.close()

# Main function
def main():
    create_database()
    start_date = input("Enter the start date (YYYY-MM-DD): ")
    end_date = input("Enter the end date (YYYY-MM-DD): ")

    try:
        datetime.strptime(start_date, "%Y-%m-%d")
        datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        print("Invalid date format. Please use YYYY-MM-DD.")
        return

    data = fetch_asteroid_data(start_date, end_date)
    if data:
        store_data_in_database(data)
        print("Data successfully fetched and stored in the database.")

    # Run analysis queries
    query_fastest_asteroids()
    query_hazardous_large_asteroids()

    # Run visualizations
    visualize_top_fastest_asteroids()
    visualize_velocity_vs_diameter()

if __name__ == "__main__":
    main()