#!/bin/bash
set -e  # Exit on error

# Ensure system is updated
apt-get update && apt-get install -y curl unzip wget jq

# Install Google Chrome
if ! command -v google-chrome-stable &> /dev/null; then
    echo "Installing Google Chrome..."
    wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor > /usr/share/keyrings/google-chrome.gpg
    echo "deb [signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" | tee /etc/apt/sources.list.d/google-chrome.list
    apt-get update && apt-get install -y google-chrome-stable
fi

# Install ChromeDriver
CHROME_VERSION=$(google-chrome-stable --version | awk '{print $3}')
API_RESPONSE=$(curl -sS https://googlechromelabs.github.io/chrome-for-testing/latest-patch-versions.json)

if ! echo "$API_RESPONSE" | jq empty > /dev/null 2>&1; then
    echo "API error. Falling back to default ChromeDriver version."
    CHROMEDRIVER_VERSION="133.0.6943.50"
else
    CHROMEDRIVER_VERSION=$(echo "$API_RESPONSE" | jq -r --arg ver "$CHROME_VERSION" '.channels.Stable[$ver] // "133.0.6943.50"')
fi

echo "Downloading ChromeDriver version $CHROMEDRIVER_VERSION..."
CHROMEDRIVER_URL="https://storage.googleapis.com/chrome-for-testing-public/$CHROMEDRIVER_VERSION/linux64/chromedriver-linux64.zip"

if curl --output /dev/null --silent --head --fail "$CHROMEDRIVER_URL"; then
    wget -q "$CHROMEDRIVER_URL"
else
    echo "ChromeDriver URL is invalid. Exiting..."
    exit 1
fi

unzip -q chromedriver-linux64.zip
mv chromedriver-linux64/chromedriver /usr/local/bin/chromedriver
chmod +x /usr/local/bin/chromedriver

echo "ChromeDriver installation completed!"
