# Use an official Python base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

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
# Copying the entire context might be too broad if build context is '.'
# Consider copying only the necessary parts if context is '.'
COPY ./src /app/src 
# If running docker-compose from root, .env is outside build context
# Environment variables are better handled via docker-compose env_file
# COPY .env . 

# Expose the port the app runs on
EXPOSE 8080

# Define the command to run the application
# Use the module path relative to WORKDIR
CMD ["/bin/bash", "-c", "init-lean.sh && python -m src.mcp_server.server"] 