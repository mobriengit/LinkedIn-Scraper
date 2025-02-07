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
        "use_captcha_solver": False  # Disabled for now
    }
else:
    default_input = input_data["value"]

search_query = default_input.get("search_query", "Small Businesses Toronto")
linkedin_cookies = json.loads(default_input.get("linkedin_cookies", "[]"))
use_proxy = default_input.get("use_proxy", True)

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

def login_linkedin(driver, cookies):
    """Logs into LinkedIn using stored cookies."""
    driver.get("https://www.linkedin.com/")
    
    for cookie in cookies:
        driver.add_cookie(cookie)
    
    driver.refresh()
    time.sleep(random.uniform(2, 5))

    # Check if login was successful
    page_title = driver.title
    if "Sign In" in page_title or page_title == "":
        print("❌ LinkedIn login failed. Check cookies.")
        return False  # Indicate failure
    else:
        print(f"✅ Successfully logged into LinkedIn. Current Page Title: {page_title}")
        return True  # Indicate success


def search_businesses(driver, query):
    """Searches LinkedIn for businesses matching the query."""
    search_url = f"https://www.linkedin.com/search/results/companies/?keywords={query}"
    driver.get(search_url)
    time.sleep(random.uniform(2, 5))

    # Print the current page title to check if we're logged in
    page_title = driver.title
    print(f"🔍 Current Page Title: {page_title}")

    if "Sign In" in page_title or page_title == "":
        print("❌ LinkedIn login failed. Exiting...")
        return None  # Return nothing if login failed

    return driver.page_source


def extract_businesses(page_source):
    """Extracts business data from LinkedIn search results and debugs elements found."""
    soup = BeautifulSoup(page_source, "html.parser")
    businesses = []

    results = soup.find_all("div", class_="entity-result")
    
    if not results:
        print("⚠️ No business elements found! LinkedIn layout might have changed.")
        with open("debug_page.html", "w", encoding="utf-8") as f:
            f.write(page_source)
        return businesses

    for result in results:
        try:
            name = result.find("span", class_="entity-result__title-text").text.strip()
            profile_link = result.find("a", class_="app-aware-link")["href"].split("?")[0]
            website = result.find("a", class_="entity-result__primary-subtitle")["href"] if result.find("a", class_="entity-result__primary-subtitle") else "N/A"
            businesses.append({"name": name, "profile_link": profile_link, "website": website})
        except AttributeError:
            continue

    return businesses

def save_to_apify(data):
    """Saves extracted business data to Apify's key-value store."""
    dataset = client.dataset("linkedin_smb_scraper")
    dataset.push_items(data)

if __name__ == "__main__":
    driver = setup_driver()

    # Ensure login works before proceeding
    if not login_linkedin(driver, linkedin_cookies):
        print("❌ Login failed. Exiting script.")
        driver.quit()
        exit(1)  # Exit script

    print(f"🔍 Searching LinkedIn for: {search_query}")
    page_source = search_businesses(driver, search_query)

    if page_source is None:
        print("❌ Search failed due to login issues. Exiting...")
        driver.quit()
        exit(1)

    businesses = extract_businesses(page_source)
    print(f"✅ Found {len(businesses)} businesses.")

    if businesses:
        save_to_apify(businesses)
        print("✅ Data saved to Apify dataset.")
    else:
        print("❌ No results found.")

    driver.quit()
