# 🛒 Amazon Price Tracker (India)

Track prices of **boAt brand** products on [Amazon.in](https://www.amazon.in) and get **email alerts** when prices drop below a defined threshold.

---

## 🔧 Features

- ✅ Scrapes product titles, prices, ratings, review counts, availability, and links
- 📉 Alerts via **email** when product prices fall below your threshold
- 📄 Saves results in **CSV** and **JSON** format
- 🔁 Runs automatically every hour using `schedule`
- 🔒 Uses random **User-Agent rotation** to avoid blocking
- 🔐 Securely loads credentials using a `.env` file
- 🪵 Detailed **logging** to `scraper.log` for debugging

---

## 📁 Project Structure

.
├── .env                      # Contains email credentials (not to be shared)  
├── product_data.json         # Latest product data in JSON  
├── scraper.log               # Log file for all scraping and email actions  
├── product_data.csv          # Latest product data in CSV    
├── price_tracker.py          # Main script  
├── README.md                 # This is the documentation or the README.md file  
└──GUIDE.md                  # This is the Guide for the web scraper project price tracker  

---

## ⚙️ Setup Instructions

### 1. 📦 Install Required Packages

Make sure you have Python 3 installed, then:

```bash
pip install -r requirements.txt
```

beautifulsoup4
pandas
numpy
requests
python-dotenv
schedule

---

### 2. 🔐 Create .env file

EMAIL=your_gmail_address@gmail.com
EMAIL_PASSWORD=your_app_password
RECEIVER_EMAIL=receiver@example.com

⚠️ Use an App Password if using Gmail with 2FA enabled.
Generate from: https://myaccount.google.com/apppasswords

---

### 3. 🚀 Run the Script

python price_tracker.py

This will:
1.Scrape the products immediately once.
2.Then run every hour in the background.

---

### 4. ✉️ Email Alert Format

- boAt Rockerz 255 Pro | ₹899.00 | In Stock  
  https://www.amazon.in/dp/B08TV2P1N8

- boAt BassHeads 100 | ₹499.00 | In Stock  
  https://www.amazon.in/dp/B07C2Y1Z1W

---

### 5.  🧠 Customization

| Feature         | How to Change                                |
| --------------- | -------------------------------------------- |
| Product Brand   | Change the `URL` in the script               |
| Price Threshold | Modify `PRICE_THRESHOLD` in the script       |
| Email Frequency | Adjust `schedule.every(1).hour` to your need |
| Output Formats  | Edit `to_csv` / `to_json` lines              |

---

### 6. 🛑 Disclaimer

-->This script is for educational use only.
-->Scraping Amazon may violate their Terms of Service.
-->Consider using the Amazon Product Advertising API for production use.

---

👨‍💻 Author
Developed by Garv Changrani (https://github.com/garvity)
