import requests
from bs4 import BeautifulSoup
import sqlite3

DB_NAME = "EPL.db"
URL = "https://en.wikipedia.org/wiki/Premier_League"

class EPLDataCollector:
    def __init__(self):
        self.url = URL
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }
        self.conn = sqlite3.connect(DB_NAME)
        self.c = self.conn.cursor()

    def __del__(self):
        self.conn.close()

    def fetch_page(self):
        response = requests.get(self.url, headers=self.headers)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")

    def create_tables(self):
        self.c.execute("""
            CREATE TABLE IF NOT EXISTS EPL_season2425 (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                club_name TEXT,
                current_standing INTEGER,
                first_season INTEGER,
                season_in_top_division INTEGER,
                season_in_PL INTEGER,
                season_in_current_spell INTEGER,
                top_division_title INTEGER,
                most_recent_top_division_title INTEGER
            )
        """)

        self.c.execute("""
            CREATE TABLE IF NOT EXISTS EPL_season2425_managers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                manager_name TEXT,
                nationality TEXT,
                club_name TEXT,
                appointed TEXT,
                time_as_manager TEXT
            )
        """)

        self.conn.commit()

        """Store the collected data into the SQLite database."""
        self.c.executemany("""
            INSERT INTO EPL_season2425 
            (name, current_standing, first_season, season_in_top_division, season_in_PL, season_in_current_spell,
            top_division_title, most_recent_top_division_title)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, clubs_data)

        self.c.executemany("""
            INSERT INTO EPL_season2425_managers 
            (manager_name, nationality, club_name, appointed, time_as_manager)
            VALUES (?, ?, ?, ?, ?)
        """, managers_data)

        self.conn.commit()

    def extract_club_data(self, soup):
        """Extract the club and manager data from the Wikipedia page."""
        tables = soup.find_all("table", class_="wikitable")
        clubs_data = []
        managers_data = []

        for table in tables:
            #Find caption with Current Premier League managers and scrape data for that table
            if table.caption and "Current Premier League managers" in table.caption.text:
                rows = table.find_all("tr")
                for row in rows[1:]:
                    columns = row.find_all("td")
                    club_name = columns[0].text.strip()
                    current_standing = int(columns[1].text.strip())
                    first_season = int(columns[2].text.strip())
                    season_in_top_division = int(columns[3].text.strip())
                    season_in_PL = int(columns[4].text.strip())
                    season_in_current_spell = int(columns[5].text.strip())
                    top_division_title = int(columns[6].text.strip())
                    most_recent_top_division_title = int(columns[7].text.strip())
                    clubs_data.append((club_name, current_standing, first_season, season_in_top_division, season_in_PL, season_in_current_spell, top_division_title, most_recent_top_division_title))

                    manager = columns[8].text.strip()


    # def query_answers(self):
    #     """Answer the queries based on the data stored in the database."""
        
    #     # a. Earliest appointed manager and last top division title
    #     self.c.execute("""
    #         SELECT manager_name, club_name, appointed, most_recent_top_division_title
    #         FROM EPL_season2425_managers
    #         ORDER BY appointed ASC LIMIT 1
    #     """)
    #     earliest_manager = self.c.fetchone()
    #     print(f"Earliest Appointed Manager: {earliest_manager[0]}, Club: {earliest_manager[1]}, Appointed: {earliest_manager[2]}, Last Top Division Title: {earliest_manager[3]}")

    #     # b. Nationality of the manager leading the club with the most top-division titles
    #     self.c.execute("""
    #         SELECT nationality, club_name
    #         FROM EPL_season2425_managers
    #         JOIN EPL_season2425 ON EPL_season2425_managers.club_name = EPL_season2425.name
    #         ORDER BY top_division_title DESC LIMIT 1
    #     """)
    #     highest_title_manager = self.c.fetchone()
    #     print(f"Nationality of Manager with Most Titles: {highest_title_manager[0]}, Club: {highest_title_manager[1]}")

    #     # c. Club with most consecutive seasons in top division, and manager appointed earliest
    #     self.c.execute("""
    #         SELECT club_name, season_in_top_division, manager_name, appointed
    #         FROM EPL_season2425
    #         JOIN EPL_season2425_managers ON EPL_season2425.name = EPL_season2425_managers.club_name
    #         ORDER BY season_in_top_division DESC LIMIT 1
    #     """)
    #     longest_staying_club = self.c.fetchone()
    #     print(f"Club with Most Consecutive Seasons: {longest_staying_club[0]}, Seasons: {longest_staying_club[1]}")
    #     print(f"Earliest Appointed Manager: {longest_staying_club[2]}, Appointed: {longest_staying_club[3]}")

if __name__ == "__main__":
    epl_collector = EPLDataCollector()
    epl_collector.create_table()
    print("Table created")


    #


    # soup = epl_collector.fetch_page()
    # clubs_data, managers_data = epl_collector.extract_club_data(soup)

    # epl_collector.store_data(clubs_data, managers_data)
    # epl_collector.query_answers()
