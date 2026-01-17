
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port (Internal is 8000, mapped to 8003 in compose)
EXPOSE 8000

# Run command
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
