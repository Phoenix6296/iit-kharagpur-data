import sqlite3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Initialize SQLite database
def initialize_database():
    conn = sqlite3.connect("amazon.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_name TEXT,
            product_name TEXT,
            price TEXT,
            rating TEXT,
            reviews TEXT,
            product_url TEXT
        )
    """)
    conn.commit()
    return conn

# Insert data into the database
def insert_into_database(conn, data):
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO products (category_name, product_name, price, rating, reviews, product_url)
        VALUES (?, ?, ?, ?, ?, ?)
    """, data)
    conn.commit()

# Initialize WebDriver
driver = webdriver.Chrome()  # Update with actual path
driver.get("https://www.amazon.in/")
driver.maximize_window()

# Initialize database
conn = initialize_database()

try:
    # Navigate to "Today's Deals"
    todays_deal = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.LINK_TEXT, "Today's Deals"))
    )
    todays_deal.click()

    # Wait for the "Today's Deals" page to load
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "slot-1")))

    # Locate the slider for categories
    slider = driver.find_element(By.CSS_SELECTOR, "div#s-refinements")
    categories = slider.find_elements(By.CSS_SELECTOR, "span.a-list-item")

    # Loop through each category
    for category in categories[:5]:  # Limit to 5 categories for demonstration
        try:
            category_name = category.text
            print(f"\nProcessing category: {category_name}")

            # Scroll to the category and click it
            ActionChains(driver).move_to_element(category).perform()
            category.click()

            # Wait for the category page to load
            time.sleep(3)

            # Fetch the first 10 products in this category
            products = driver.find_elements(By.CSS_SELECTOR, "div.a-section.a-spacing-none")
            for product in products[:10]:
                try:
                    # Extract product details
                    product_name = product.find_element(By.CSS_SELECTOR, "span.a-text-normal").text
                    price = product.find_element(By.CSS_SELECTOR, "span.a-price-whole").text
                    rating = product.find_element(By.CSS_SELECTOR, "span.a-icon-alt").text if product.find_elements(By.CSS_SELECTOR, "span.a-icon-alt") else "N/A"
                    reviews = product.find_element(By.CSS_SELECTOR, "span.a-size-base").text if product.find_elements(By.CSS_SELECTOR, "span.a-size-base") else "N/A"
                    product_url = product.find_element(By.CSS_SELECTOR, "a").get_attribute("href")

                    # Print details (for debugging)
                    print(f"Product: {product_name}, Price: {price}, Rating: {rating}, Reviews: {reviews}, URL: {product_url}")

                    # Store details in the database
                    insert_into_database(conn, (category_name, product_name, price, rating, reviews, product_url))

                except Exception as e:
                    print(f"Error extracting product details: {e}")

        except Exception as e:
            print(f"Error with category {category.text}: {e}")

        # Go back to the "Today's Deals" page
        driver.back()
        time.sleep(2)

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # Close the browser and database connection
    driver.quit()
    conn.close()