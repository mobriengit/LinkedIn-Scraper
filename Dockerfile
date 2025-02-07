# Use Apify’s Python image
FROM apify/actor-python:3.9

# Set working directory
WORKDIR /app

# Install system dependencies required for Selenium and Chrome
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    curl \
    jq \  # ✅ Install jq to parse JSON
    xvfb \
    libxi6 \
    libgconf-2-4 \
    libnss3 \
    libxss1 \
    libappindicator1 \
    fonts-liberation \
    libgbm1 \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Install Google Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor > /usr/share/keyrings/google-chrome-keyring.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && apt-get install -y google-chrome-stable

# Install ChromeDriver (matching the installed Chrome version)
RUN CHROME_VERSION=$(google-chrome-stable --version | awk '{print $3}') && \
    CHROMEDRIVER_VERSION=$(curl -sS https://googlechromelabs.github.io/chrome-for-testing/latest-patch-versions.json | jq -r --arg ver "$CHROME_VERSION" '.channels.Stable[$ver]') && \
    wget -q "https://storage.googleapis.com/chrome-for-testing-public/$CHROMEDRIVER_VERSION/linux64/chromedriver-linux64.zip" && \
    unzip chromedriver-linux64.zip && \
    mv chromedriver-linux64/chromedriver /usr/local/bin/chromedriver && \
    chmod +x /usr/local/bin/chromedriver

# Verify Chrome and ChromeDriver installation
RUN google-chrome-stable --version && chromedriver --version

# Copy project files
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Start script
CMD ["python", "main.py"]

