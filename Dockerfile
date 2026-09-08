# Multi-stage Python 3.11 Slim Container
FROM python:3.11-slim

# Set working directory and environment flags
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Run automated tests during container build to ensure integrity
RUN pytest tests/

# Expose default port
EXPOSE 8000

# Run unified gateway
CMD ["python", "main.py"]
