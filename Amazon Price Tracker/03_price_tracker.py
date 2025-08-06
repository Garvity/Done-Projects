# ========== Price Tracker Script for Amazon India ==========

# ========== Import Required Libraries ==========
import logging
import requests
from bs4 import BeautifulSoup
import pandas as pd 
import numpy as np
import smtplib
from email.mime.multipart import MIMEMultipart #MIME (Multipurpose Internet Mail Extensions) is a standard that extends the format of email messages to support text in character sets other than ASCII, as well as attachments of audio, video, images, and application programs.
from email.mime.text import MIMEText
import schedule
import time
import os
from dotenv import load_dotenv

# ========== Configuration Setup ==========

# Load environment variables from .env file
load_dotenv()

# Email credentials and receiver
EMAIL = os.getenv("EMAIL")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")

# Price threshold for sending alerts
PRICE_THRESHOLD = 1500  # INR

# List of fake user agents to avoid detection and rotate headers
USER_AGENTS = [
    # Chrome on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    
    # Firefox on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0",
    
    # Edge on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0",
    
    # Safari on macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5_2) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
    
    # Chrome on macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.208 Safari/537.36",
    
    # Chrome on Android
    "Mozilla/5.0 (Linux; Android 12; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36",
    
    # Safari on iPhone
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Mobile/15E148 Safari/604.1",
    
    # Firefox on Linux
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:127.0) Gecko/20100101 Firefox/127.0",
    
    # Chrome on Linux
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    
    # Samsung Internet on Android
    "Mozilla/5.0 (Linux; Android 13; SAMSUNG SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/25.0 Chrome/116.0.5845.163 Mobile Safari/537.36",
]

# HTTP headers for requests
HEADERS = {
    "User-Agent": np.random.choice(USER_AGENTS),
    "Accept-Language": "en-US,en;q=0.5"
}

# Amazon search URL for boAt brand products
URL = "https://www.amazon.in/s?bbn=1388921031&rh=n%3A1388921031%2Cp_89%3AboAt&_encoding=UTF8&content-id=amzn1.sym.82b20790-8877-4d70-8f73-9d8246e460aa&pd_rd_r=b5331660-daba-4096-99f4-8447a2ec81be&pd_rd_w=oE2Er&pd_rd_wg=0p3rl&pf_rd_p=82b20790-8877-4d70-8f73-9d8246e460aa&pf_rd_r=89MZD515G6RNWWHZWPSP&ref=pd_hp_d_atf_unk"

# ========== Logging Setup ==========
logging.basicConfig(
    level=logging.INFO,  # sets the logging level to INFO like INFO, WARNING, ERROR, CRITICAL, DEBUG 
    format="%(asctime)s [%(levelname)s] %(message)s", #for time stamps and log levels
    handlers=[
        logging.FileHandler("scraper.log", mode="a"), # Displays log messages in a file named scraper.log and appends the messages
        logging.StreamHandler() # Displays log messages in the console
    ]
)

# ========== Product Detail Extractors ==========

# Extract product title
def get_title(soup):
    try:
        title = soup.find("span", attrs={"id": 'productTitle'})
        title_string = title.text.strip()
        logging.info(f"Fetched title: {title_string}")
    except AttributeError:
        title_string = ""
        logging.warning("Title not found.")
    return title_string

# Extract product price
def get_price(soup):
    try:
        price = soup.find("span", class_="a-price-whole").get_text(strip=True)
        price = float(price.replace(",", ""))
        logging.info(f"Fetched price: ₹{price}")
        return price
    except (AttributeError, ValueError):
        logging.warning("Price not found or invalid.")
        return None

# Extract product rating
def get_rating(soup):
    try:
        rating = soup.find("i", class_="a-icon a-icon-star a-star-4-5").string.strip()
    except AttributeError:
        try:
            rating = soup.find("span", class_="a-icon-alt").string.strip()
        except:
            rating = ""
            logging.warning("Rating not found.")
    return rating

# Extract review count
def get_review_count(soup):
    try:
        return soup.find("span", attrs={'id': 'acrCustomerReviewText'}).string.strip()
    except AttributeError:
        logging.warning("Review count not found.")
        return ""

# Extract availability status
def get_availability(soup):
    try:
        available = soup.find("div", attrs={'id': 'availability'})
        available = available.find("span").string.strip()
    except AttributeError:
        available = "Not Available"
        logging.warning("Availability not found.")
    return available

# ========== Email Alert Function ==========

# Send email if products are below the price threshold
def send_price_alert(matching_df):
    if matching_df.empty:
        logging.info("No products below threshold to alert.")
        return

    try:
        subject = "🔔 Amazon Price Drop Alert"
        body = f"The following products are below ₹{PRICE_THRESHOLD} for earbuds in Amazon India:\n\n"

        for _, row in matching_df.iterrows(): #indexing through DataFrame rows
            # Format each product's details
            body += f"- {row['title']} | {row['price']} | {row['availability']}\n  {row['url']}\n\n"

        msg = MIMEMultipart() #Creating a multipart message object for email including plain text,Html,images,attachments etc.
        msg['From'] = EMAIL     # Sender's email address
        msg['To'] = RECEIVER_EMAIL  # Receiver's email address
        msg['Subject'] = subject    # Subject of the email

        """ Attaching a plain text message body to your email,
            Creates a MIME (Multipurpose Internet Mail Extensions) object that contains the email body text.
            'plain' specifies that the content is plain text, not HTML."""
        msg.attach(MIMEText(body, 'plain'))

        """Establishes a secure SSL-encrypted(Secure Socket Layer) connection to Gmail’s SMTP server.(Simple Mail Transfer Protocol)
            smtp.gmail.com is the Gmail SMTP server.
            465 is the port used for SMTP over SSL.
            The with statement ensures the connection is automatically closed after use."""
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL, EMAIL_PASSWORD)
            server.sendmail(EMAIL, RECEIVER_EMAIL, msg.as_string())

        logging.info("✅ Price alert email sent.")
    except Exception as e:
        logging.error(f"❌ Failed to send email: {e}")

# ========== Main Scraper Function ==========

# Scrape Amazon listings and check prices
def scrape_data():
    logging.info("🔍 Starting Amazon scraper...")

    try:
        # Request product listing page (HTTP GET request)
        webpage = requests.get(URL, headers=HEADERS, timeout=5)

        # BeautifulSoup object to parse the HTML content in python,webpage.content is the HTML content of the page in bytes
        soup = BeautifulSoup(webpage.content, "html.parser") 

        # Extract product links
        links = soup.find_all("a", class_='a-link-normal s-line-clamp-4 s-link-style a-text-normal')
        links_list = [link.get('href') for link in links]
        logging.info(f"🧲 Found {len(links_list)} product links.")

    except Exception as e:
        logging.error(f"❌ Failed to load product listing page: {e}")
        return

    # Initialize data dictionary
    d = {"title": [], "price": [], "rating": [], "reviews": [], "availability": [], "url": []}

    # Iterate through each product link
    for link in links_list:
        full_url = "https://www.amazon.in" + link
        logging.info(f"Scraping: {full_url}")
        try:
            product_page = requests.get(full_url, headers=HEADERS, timeout=5)
            product_soup = BeautifulSoup(product_page.content, "html.parser")

            # Extract product details
            title = get_title(product_soup)
            price = get_price(product_soup)
            rating = get_rating(product_soup)
            reviews = get_review_count(product_soup)
            availability = get_availability(product_soup)

            # Append to dictionary
            d["title"].append(title)
            d["price"].append(price)
            d["rating"].append(rating)
            d["reviews"].append(reviews)
            d["availability"].append(availability)
            d["url"].append(full_url)

        except Exception as e:
            logging.error(f"❌ Error scraping product: {e}")

    # Convert dictionary to DataFrame and clean
    product_df = pd.DataFrame(d)
    product_df = product_df.dropna(subset=['title', 'price'])

    # Format price and convert to numeric for filtering
    product_df['numeric_price'] = product_df['price'].astype(float)
    product_df['price'] = product_df['numeric_price'].apply(lambda x: f"₹{x:,.2f}")

    # Save data to CSV and JSON
    product_df.to_csv("product_data.csv", index=False) #index=False treats the first column index as seperate column
    product_df.to_json("product_data.json", orient="records", indent=2, force_ascii=False) 

    # Filter products below the threshold
    matching = product_df[product_df['numeric_price'] <= PRICE_THRESHOLD]
    matching = matching.reset_index(drop=True)

    # Send alerts if matches found
    if not matching.empty:
        logging.info(f"Found {len(matching)} products below ₹{PRICE_THRESHOLD}. Sending alerts...")
    else:
        logging.info("No products found below the price threshold.")

    send_price_alert(matching)
    logging.info("✅ Scraping cycle completed.\n")

# ========== Scheduler ==========
if __name__ == "__main__":
    # Run scraper immediately once
    scrape_data()

    # Schedule scraper to run every hour
    schedule.every(1).hour.do(scrape_data)

    logging.info("⏳ Scheduler started. Scraping every 1 hour.")
    print("⏳ Scheduler started. Press Ctrl+C to stop.")

    # Run scheduler loop
    while True:
        schedule.run_pending() # Run scheduled tasks
        time.sleep(60) #used to avoid busy-waiting,constant polling and consuming CPU resources
