# Use official Playwright Python base image (includes Chromium and all system deps)
FROM mcr.microsoft.com/playwright/python:v1.49.1-jammy

# Set working directory
WORKDIR /app

# Install Node.js and npm (required by rfbrowser init)
RUN apt-get update && apt-get install -y curl gnupg \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Initialize RF Browser (installs browser binaries and system deps)
RUN rfbrowser init && npx playwright install-deps chromium

# Copy the rest of the application
COPY . .

# Expose port
EXPOSE 8000

# Start command
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
