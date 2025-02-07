LinkedIn Scraper 🚀
A Python-based LinkedIn business scraper that extracts business details using Selenium, BeautifulSoup, and Apify. This tool automates searches and retrieves data from LinkedIn.

📌 Features
Automated LinkedIn search for businesses.
Scrapes business profiles, websites, and emails.
Uses proxies (Apify Proxy) for anonymity.
Bypasses CAPTCHAs with 2Captcha.
Saves results to Apify’s Key-Value Store.
🛠 Setup Instructions
1️⃣ Clone the Repository
bash
Copy
Edit
git clone https://github.com/mobriengit/LinkedIn-Scraper.git
cd LinkedIn-Scraper
2️⃣ Install Dependencies
bash
Copy
Edit
pip install -r requirements.txt
3️⃣ Set Up Environment Variables
Create a .env file in the project root with:

ini
Copy
Edit
APIFY_TOKEN=your_apify_api_token
TWO_CAPTCHA_API_KEY=your_2captcha_api_key
4️⃣ Run the Scraper
Using Local Machine
bash
Copy
Edit
python main.py
Using Docker
bash
Copy
Edit
docker build -t linkedin-scraper .
docker run --rm -e APIFY_TOKEN=your_apify_api_token -e TWO_CAPTCHA_API_KEY=your_2captcha_api_key linkedin-scraper
🔧 Configuration
Modify config.json (if applicable) or set environment variables:

Parameter	Description	Default Value
search_query	Search term for LinkedIn	"Small Businesses Toronto"
linkedin_cookies	LinkedIn session cookies (JSON format)	"[]"
use_proxy	Enable Apify Proxy (recommended)	True
use_captcha_solver	Solve CAPTCHAs using 2Captcha	True
📦 Output
Scraped results are saved in Apify’s Key-Value Store and can be accessed via Apify UI or API.

Example output:

json
Copy
Edit
[
  {
    "name": "Example Business",
    "profile_link": "https://www.linkedin.com/company/example/",
    "website": "https://example.com",
    "email": "contact@example.com"
  }
]
🛠 Debugging
Check Chrome Installation
If you see NoSuchDriverException:

bash
Copy
Edit
which google-chrome-stable
google-chrome-stable --version
If not found, re-run the Docker build or install Chrome manually.

Check Apify API
bash
Copy
Edit
curl -X GET "https://api.apify.com/v2/key-value-stores" -H "Authorization: Bearer YOUR_APIFY_TOKEN"
If you get an authentication error, double-check your API key.

📜 License
MIT License. See LICENSE for details.

💡 Need Help?
Open an issue on GitHub Issues.
Contact me on LinkedIn/Twitter/X.
