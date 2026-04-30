# Use Python 3.11 slim (minimal version) image as base
FROM python:3.11-slim

# Set working directory inside container - everything executed inside the app folder
WORKDIR /app

# Install libgomp for OpenMP (required by LightGBM)
RUN apt-get update && \
    apt-get install -y --no-install-recommends libgomp1 && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first to the working directory (for Docker layer caching)
COPY serving/requirements.txt .

# Install Python dependencies (smaller image size without saving cache)
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code to the working directory
COPY serving/app.py .

# Copy model files
COPY models/ ./models/

# Expose port 8000 (using docker run anyway)
EXPOSE 8000

# Run uvicorn server
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]