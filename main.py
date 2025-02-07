pip install selenium beautifulsoup4 apify-client

import time
import random
import json
import os
from apify_client import ApifyClient
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Set up Apify storage
APIFY_TOKEN = os.getenv("APIFY_TOKEN")
client = ApifyClient(APIFY_TOKEN)

def setup_driver():
    """Configures a stealth Chrome WebDriver for Apify."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver

def login_linkedin(driver, cookies):
    """Logs into LinkedIn using stored cookies."""
    driver.get("https://www.linkedin.com/")
    for cookie in cookies:
        driver.add_cookie(cookie)
    driver.refresh()
    time.sleep(random.uniform(2, 5))

def search_profiles(driver, query):
    """Searches LinkedIn for profiles based on a query."""
    search_url = f"https://www.linkedin.com/search/results/people/?keywords={query}"
    driver.get(search_url)
    time.sleep(random.uniform(2, 5))
    return driver.page_source

def extract_profiles(page_source):
    """Extracts profile data from LinkedIn search results."""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(page_source, "html.parser")
    profiles = []

    results = soup.find_all("div", class_="entity-result")
    for result in results:
        try:
            name = result.find("span", class_="entity-result__title-text").text.strip()
            profile_link = result.find("a", class_="app-aware-link")["href"].split("?")[0]
            title = result.find("div", class_="entity-result__primary-subtitle").text.strip()
            company = result.find("div", class_="entity-result__secondary-subtitle").text.strip()
            profiles.append({"name": name, "profile_link": profile_link, "title": title, "company": company})
        except AttributeError:
            continue
    return profiles

def save_to_apify(data):
    """Saves extracted data to Apify's key-value store."""
    dataset = client.dataset("linkedin_scraper")
    dataset.push_items(data)

if __name__ == "__main__":
    driver = setup_driver()
    cookies = []  # Load manually extracted LinkedIn cookies here
    login_linkedin(driver, cookies)

    search_query = "Data Engineers Toronto"
    print(f"Searching LinkedIn for: {search_query}")
    page_source = search_profiles(driver, search_query)

    profiles = extract_profiles(page_source)
    print(f"Found {len(profiles)} profiles.")

    if profiles:
        save_to_apify(profiles)
        print("Data saved to Apify dataset.")
    else:
        print("No results found.")

    driver.quit()
