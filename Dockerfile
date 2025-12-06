FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create data directories
RUN mkdir -p data/output logs

# Make startup script executable and run both services
RUN chmod +x start.sh
CMD ["./start.sh"]



