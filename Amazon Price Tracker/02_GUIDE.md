
📘 Amazon Price Tracker – Usage Guide
--------------------------------------

📌 Overview:
This Python script tracks product prices on Amazon India for a specified brand (`boAt` in the current config).
If the price drops below a set threshold, it sends an email alert with product details.

🚀 Setup Instructions
---------------------

1. Clone or Copy the Script:
   Save the script file as `price_tracker.py` in your working directory.

2. Install Required Libraries:
   Use a virtual environment and install dependencies:

   ```bash
   python -m venv venv
   source venv/bin/activate      # macOS/Linux
   venv\Scripts\activate       # Windows

   pip install -r requirements.txt
   ```

   `requirements.txt` should contain:
   requests
   beautifulsoup4
   pandas
   numpy
   python-dotenv
   schedule

3. Create `.env` File:
   Add your email credentials and recipient in the same directory:

   EMAIL = youremail@gmail.com
   EMAIL_PASSWORD = yourpassword
   RECEIVER_EMAIL = receiver@example.com

4. Run the Script:
   ```bash
   python price_tracker.py
   ```

   It will run once immediately and then every hour.

⚙️ Configuration Options
------------------------

- `PRICE_THRESHOLD = 1500`: Change this to set your target price.
- `URL`: Update the Amazon India URL for different brands or categories.
- `USER_AGENTS`: Rotates between user agents to avoid detection.

📤 Output Files
---------------

- `product_data.csv`: Stores the scraped product data in tabular format.
- `product_data.json`: Stores the same data in JSON format.
- `scraper.log`: Logs the script's activity for debugging.

📧 Email Alerts
---------------

If products under the price threshold are found, the script sends an email like:

Subject: 🔔 Amazon Price Drop Alert

The following products are below ₹1500:

- boAt Rockerz 255 | ₹899.00 | In Stock
  https://www.amazon.in/...

🛠 Troubleshooting
------------------

- **503 Errors**: Amazon may block requests; the script randomizes headers to reduce risk.
- **No Email Sent**: Check `.env` values or Gmail security settings (e.g., enable "App Passwords").
- **Empty CSV/JSON**: The product links might not be valid; try changing the listing page URL.

🕑 Scheduling
-------------

- Currently uses the `schedule` module to run every 1 hour.
- You can modify `schedule.every(1).hour` to:
  schedule.every(10).minutes
  schedule.every().day.at("10:30")

📌 Note
-------

- Do **not** run the script too frequently, or Amazon may block your IP.
- This is for educational use only. For production use, consider Amazon’s Product Advertising API.