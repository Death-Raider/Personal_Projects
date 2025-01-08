# Base Python image
FROM python:3.11-slim

# Install necessary dependencies
RUN apt-get update -qq -y && apt-get install -y --no-install-recommends \
    wget \
    unzip \
    libx11-dev \
    libx264-dev \
    libasound2 \
    libatk-bridge2.0-0 \
    libgtk-4-1 \
    libnss3 \
    libxss1 \
    libnspr4 \
    fonts-liberation \
    libgbm1 \
    libxrandr2 \
    libxcomposite1 \
    libatspi2.0-0 \
    libappindicator3-1\
    xdg-utils

RUN wget https://storage.googleapis.com/chrome-for-testing-public/131.0.6778.204/linux64/chrome-linux64.zip -P /tmp && \
    unzip /tmp/chrome-linux64.zip -d /opt && \
    rm /tmp/chrome-linux64.zip

RUN wget https://storage.googleapis.com/chrome-for-testing-public/131.0.6778.204/linux64/chromedriver-linux64.zip -P /tmp && \
    unzip /tmp/chromedriver-linux64.zip -d /opt && \
    rm /tmp/chromedriver-linux64.zip

ENV CHROME_BIN=/opt/chrome-linux64/chrome
ENV CHROMEDRIVER_PATH=/opt/chromedriver-linux64/chromedriver
ENV PATH=$PATH:$CHROMEDRIVER_PATH
ENV PATH=$PATH:$CHROME_BIN

RUN chmod +x /opt/chromedriver-linux64/chromedriver

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
