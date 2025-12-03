# Use Python 3.11 base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy bot code
COPY bot.py .

# Set environment variable placeholder (will override in Railway)
ENV BOT_TOKEN=""

# Run bot
CMD ["python", "bot.py"]
