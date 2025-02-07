# Use Apify’s Python image
FROM apify/actor-python:3.9

# Install Tor
# RUN apt-get update && apt-get install -y tor

# Set working directory
WORKDIR /app

# Copy all project files to the container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Start Tor service
CMD service tor start && python main.py
