# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose Flask default port
EXPOSE 5000

# Set environment variable for Flask
ENV FLASK_APP=shoppingcart.py

# Start the Flask app
CMD ["flask", "run", "--host=0.0.0.0"]