FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    wget curl unzip jq gnupg2 \
    libvulkan1 \
    libglib2.0-0 libnss3 libgconf-2-4 libfontconfig1 \
    libx11-6 libxext6 libxrender1 libxtst6 libxi6 \
    libxrandr2 libxfixes3 libasound2 libatk1.0-0 \
    libatk-bridge2.0-0 libcups2 libgtk-3-0 libxss1 \
    fonts-liberation xdg-utils \
    gcc libpq-dev python3-dev build-essential \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt-get install -y ./google-chrome-stable_current_amd64.deb && \
    rm google-chrome-stable_current_amd64.deb

RUN set -eux; \
    CHROME_VERSION=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+\.\d+'); \
    CHROMEDRIVER_VERSION=$(curl -s https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json \
        | jq -r ".channels.Stable.version"); \
    wget -q "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/${CHROMEDRIVER_VERSION}/linux64/chromedriver-linux64.zip"; \
    unzip chromedriver-linux64.zip; \
    mv chromedriver-linux64/chromedriver /usr/bin/chromedriver; \
    chmod +x /usr/bin/chromedriver; \
    rm -rf chromedriver-linux64*

RUN pip install uv

COPY pyproject.toml /app/pyproject.toml
WORKDIR /app

RUN uv pip install --system .

COPY spider.py /app/spider.py


