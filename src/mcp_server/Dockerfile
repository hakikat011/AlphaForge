# Use an official Python base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install LEAN CLI
RUN pip install --no-cache-dir lean

# Add initialization script
COPY scripts/init-lean.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/init-lean.sh

# Copy the application source code into the container
COPY ./src /app/src
COPY ./config /app/config

# Set Python path
ENV PYTHONPATH=/app

# Expose the port the app runs on
EXPOSE 8080

# Define the command to run the application
CMD ["/bin/bash", "-c", "init-lean.sh && python -m src.mcp_server.server"]