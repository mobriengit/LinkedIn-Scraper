import os
import json
import time
import random
import re
import requests
from apify_client import ApifyClient
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

# Load input parameters from Apify
APIFY_TOKEN = os.getenv("APIFY_TOKEN")
client = ApifyClient(APIFY_TOKEN)
input_data = client.key_value_store("default").get_record("INPUT")

if input_data is None or "value" not in input_data:
    print("⚠️ Warning: No input data found in Apify. Using default values.")
    default_input = {
        "search_query": "Small Businesses Toronto",
        "linkedin_cookies": "[]",
        "use_proxy": True,
        "use_captcha_solver": False  # Disabled CAPTCHA solver
    }
else:
    default_input = input_data["value"]

search_query = default_input.get("search_query", "Small Businesses Toronto")
linkedin_cookies = json.loads(default_input.get("linkedin_cookies", "[]"))
use_proxy = default_input.get("use_proxy", True)
use_captcha_solver = False  # Ensuring CAPTCHA solver is OFF

CHROMIUM_PATH = "/usr/bin/google-chrome-stable"
CHROMEDRIVER_PATH = "/usr/local/bin/chromedriver"

def setup_driver():
    """Configures a stealth Chrome WebDriver with Apify proxy."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    
    if use_proxy:
        chrome_options.add_argument("--proxy-server=http://proxy.apify.com:8000")
    
    chrome_options.binary_location = CHROMIUM_PATH
    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def solve_captcha(image_url):
    """Bypasses CAPTCHA solving (disabled)."""
    print("⚠️ CAPTCHA solver disabled.")
    return None

def login_linkedin(driver, cookies):
    """Logs into LinkedIn using stored cookies."""
    driver.get("https://www.linkedin.com/")
    for cookie in cookies:
        driver.add_cookie(cookie)
    driver.refresh()
    time.sleep(random.uniform(2, 5))

def search_businesses(driver, query):
    """Searches LinkedIn for businesses matching SMB criteria."""
    search_url = f"https://www.linkedin.com/search/results/companies/?keywords={query}"
    driver.get(search_url)
    time.sleep(random.uniform(2, 5))
    return driver.page_source

def extract_businesses(page_source):
    """Extracts business data including emails from LinkedIn search results."""
    soup = BeautifulSoup(page_source, "html.parser")
    businesses = []

    results = soup.find_all("div", class_="entity-result")
    for result in results:
        try:
            name = result.find("span", class_="entity-result__title-text").text.strip()
            profile_link = result.find("a", class_="app-aware-link")["href"].split("?")[0]
            website = result.find("a", class_="entity-result__primary-subtitle")["href"] if result.find("a", class_="entity-result__primary-subtitle") else "N/A"
            email = scrape_email_from_website(website) if website != "N/A" else "N/A"
            businesses.append({"name": name, "profile_link": profile_link, "website": website, "email": email})
        except AttributeError:
            continue
    return businesses

def scrape_email_from_website(website):
    """Extracts contact email from business websites."""
    try:
        response = requests.get(website, timeout=5)
        if response.status_code == 200:
            emails = set(re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', response.text))
            return list(emails)[0] if emails else "N/A"
    except:
        return "N/A"

def save_to_apify(data):
    """Saves extracted business data to Apify's key-value store."""
    dataset = client.dataset("linkedin_smb_scraper")
    dataset.push_items(data)

if __name__ == "__main__":
    driver = setup_driver()
    login_linkedin(driver, linkedin_cookies)

    print(f"🔍 Searching LinkedIn for: {search_query}")
    page_source = search_businesses(driver, search_query)

    print("⚠️ Skipping CAPTCHA solver.")  # Ensuring CAPTCHA is not triggered

    businesses = extract_businesses(page_source)
    print(f"✅ Found {len(businesses)} businesses.")

    if businesses:
        save_to_apify(businesses)
        print("📦 Data saved to Apify dataset.")
    else:
        print("❌ No results found.")

    driver.quit()

