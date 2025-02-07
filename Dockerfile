# Use Apify’s official Python image
FROM apify/actor-python:3.9

# Set working directory inside the container
WORKDIR /app

# Copy all project files to the container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Define the default command to run the scraper
CMD ["python", "main.py"]
