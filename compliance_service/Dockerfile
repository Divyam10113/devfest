FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port (Internal 8003)
EXPOSE 8003

# Run command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8003"]
