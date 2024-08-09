# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Ensure pip is installed (this step is crucial for slim images)
RUN apt-get update && apt-get install -y \
    python3-pip \
    ffmpeg \
    && apt-get clean

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV DISCORD_BOT_TOKEN=MTIwMzMyNzcxODQ5NDcwNzcyMg.GctaCf.hjvUUvQQ2O38v9jnV0zRRQGEk-YrDHho2eBsgI

# Run bot.py when the container launches
CMD ["python3", "bot.py"]
