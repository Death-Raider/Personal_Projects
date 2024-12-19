# Base Python image
FROM python:3.11-slim

# Install necessary dependencies
RUN apt-get update -qq -y && apt-get install -y --no-install-recommends \
    wget \
    curl \
    unzip \
    libasound2 \
    libatk-bridge2.0-0 \
    libgtk-4-1 \
    libnss3 \
    xdg-utils

# Install Google Chrome (hardcoded version: 121-0-6167-85)
RUN wget -q -O chrome-linux64.zip https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/121.0.6167.85/linux64/chrome-linux64.zip && \
    unzip chrome-linux64.zip && \
    rm chrome-linux64.zip && \
    mv chrome-linux64 /opt/chrome/ && \
    ln -s /opt/chrome/chrome /usr/local/bin/chrome

# Install ChromeDriver (hardcoded version: 121-0-6167-85)
RUN wget -q -O chromedriver-linux64.zip https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/131.0.6778.204/linux64/chromedriver-linux64.zip && \
    unzip chromedriver-linux64.zip && \
    rm chromedriver-linux64.zip && \
    mv chromedriver-linux64/chromedriver /usr/local/bin/chromedriver && \
    chmod +x /usr/local/bin/chromedriver && \
    rm -rf chromedriver-linux64
# Install Python packages
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy your application code
COPY . /app
WORKDIR /app

# Expose FastAPI app
EXPOSE 8000

# Command to run the app
CMD ["python", "api.py"]
