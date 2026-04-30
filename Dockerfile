# Globex (GBX) Blockchain - Production Docker Image
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY *.py ./
COPY tests/ ./tests/
COPY data/ ./data/ 2>/dev/null || true

# Create data directory
RUN mkdir -p /app/data

# Expose ports
# 8080 - Dashboard API
# 5000 - P2P Network
EXPOSE 8080 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/health')" || exit 1

# Run the node
CMD ["python", "node.py"]
