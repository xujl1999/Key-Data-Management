# Use Python 3.11 as base
FROM python:3.11-slim

# Install system dependencies: curl (for installing Node/rclone), unzip
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js (LTS version)
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs

# Install rclone
RUN curl https://rclone.org/install.sh | bash

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose the API port
EXPOSE 8001

# Set entrypoint
chmod +x scripts/entrypoint.sh
ENTRYPOINT ["/bin/bash", "scripts/entrypoint.sh"]
