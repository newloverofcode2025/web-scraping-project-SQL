import requests
from bs4 import BeautifulSoup
import sqlite3
import os

# Base URL of the website to scrape
base_url = 'http://books.toscrape.com/'

# Function to create the SQLite database and table
def create_database():
    conn = sqlite3.connect('../data/products.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            price TEXT,
            rating TEXT,
            image_url TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Function to insert data into the database
def insert_product(product):
    conn = sqlite3.connect('../data/products.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO products (title, price, rating, image_url)
        VALUES (?, ?, ?, ?)
    ''', (product['title'], product['price'], product['rating'], product['image_url']))
    conn.commit()
    conn.close()

# Function to scrape a single page
def scrape_page(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes
    except requests.RequestException as e:
        print(f"Error fetching the URL: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    products = []

    # Find all product items on the page
    for article in soup.find_all('article', class_='product_pod'):
        title = article.h3.a['title']
        price = article.find('p', class_='price_color').text
        rating = article.find('p', class_='star-rating')['class'][1]
        image_url = base_url + article.find('img')['src'].replace('../', '')

        products.append({
            'title': title,
            'price': price,
            'rating': rating,
            'image_url': image_url
        })

    return products

# Function to scrape multiple pages
def scrape_books(start_page, num_pages):
    products = []
    for i in range(start_page, start_page + num_pages):
        url = f'{base_url}catalogue/page-{i}.html'
        print(f'Scraping page {i}: {url}')
        products.extend(scrape_page(url))
    return products

# Main function to run the scraper
def main():
    create_database()
    start_page = 1
    num_pages = 5  # Number of pages to scrape
    products = scrape_books(start_page, num_pages)

    for product in products:
        insert_product(product)

    print('Scraping complete. Data saved to products.db')

if __name__ == '__main__':
    main()