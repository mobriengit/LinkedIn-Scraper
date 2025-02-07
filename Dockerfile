# Use Apify’s Python image
FROM apify/actor-python:3.9

# Set working directory
WORKDIR /app

# Copy all project files to the container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Start script
CMD ["python", "main.py"]
