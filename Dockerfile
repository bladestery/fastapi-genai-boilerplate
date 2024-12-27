# Use a specific version of Python slim image
FROM python:3.12-slim-bullseye

# Set the working directory
WORKDIR /app

# Install system dependencies and clean up in a single RUN command
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    supervisor \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Upgrade pip and install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy only necessary files
COPY . /app

# Expose the port the app runs on
EXPOSE 8001

# Run the application
CMD ["python", "main.py"]