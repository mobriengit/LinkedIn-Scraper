#!/bin/bash
set -e  # Exit on error

echo "🔹 Updating system and installing dependencies..."
apt-get update && apt-get install -y curl unzip wget jq gnupg

echo "🔹 Installing Google Chrome..."
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor > /usr/share/keyrings/google-chrome-keyring.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list
apt-get update && apt-get install -y google-chrome-stable

echo "✅ Google Chrome Installed: $(google-chrome-stable --version)"

# Fetch Chrome version
CHROME_VERSION=$(google-chrome-stable --version | awk '{print $3}')
echo "🔹 Chrome Version Detected: $CHROME_VERSION"

# Fetch ChromeDriver version
echo "🔹 Fetching ChromeDriver version..."
CHROMEDRIVER_VERSION=$(curl -s "https://googlechromelabs.github.io/chrome-for-testing/latest-patch-versions-per-build.json" | jq -r --arg ver "$CHROME_VERSION" '.builds[$ver]')

if [[ -z "$CHROMEDRIVER_VERSION" || "$CHROMEDRIVER_VERSION" == "null" ]]; then
    echo "❌ API did not return a valid ChromeDriver version. Using fallback..."
    CHROMEDRIVER_VERSION="$CHROME_VERSION"
fi

echo "✅ ChromeDriver Version Determined: $CHROMEDRIVER_VERSION"

# Construct the ChromeDriver URL
CHROMEDRIVER_URL="https://storage.googleapis.com/chrome-for-testing-public/$CHROMEDRIVER_VERSION/linux64/chromedriver-linux64.zip"

# Check if the ChromeDriver URL is valid
if curl --output /dev/null --silent --head --fail "$CHROMEDRIVER_URL"; then
    echo "🔹 Downloading ChromeDriver..."
    wget -q "$CHROMEDRIVER_URL"
else
    echo "❌ Error: ChromeDriver URL is invalid. Exiting..."
    exit 1
fi

# Extract and install ChromeDriver
echo "🔹 Extracting ChromeDriver..."
unzip -q chromedriver-linux64.zip
mv chromedriver-linux64/chromedriver /usr/local/bin/chromedriver
chmod +x /usr/local/bin/chromedriver

# Cleanup
rm -rf chromedriver-linux64.zip chromedriver-linux64

# Verify installation
echo "✅ Chrome and ChromeDriver Setup Complete!"
google-chrome-stable --version
chromedriver --version
