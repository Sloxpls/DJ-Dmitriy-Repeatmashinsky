# Use the official Python slim image as the base image
FROM python:3.9-slim

# Set the working directory inside the container to /app
WORKDIR /app

# Copy the 'src' folder content into the /app directory in the container
COPY src/ /app/

# Update the package list and install required packages
# Install ffmpeg and python3-pip, then clean up apt cache to keep the image size small
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies from requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

# Set the command to run your bot script
CMD ["python3", "bot.py"]
