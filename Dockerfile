# Use Apify’s Python image
FROM apify/actor-python:3.9

# Set working directory
WORKDIR /app

# Install system dependencies required for Selenium and Chrome
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    curl \
    jq \
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

# Copy the setup script with the correct filename
COPY setup_chromedrive.sh /setup_chromedrive.sh

# Ensure the script is executable
RUN chmod +x /setup_chromedrive.sh

# Run the script to install Chrome and ChromeDriver
RUN /setup_chromedrive.sh

# Verify Chrome and ChromeDriver installation
RUN google-chrome-stable --version && chromedriver --version

# Copy project files
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Start script
CMD ["python", "main.py"]
