# Use official Python runtime
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install Node.js
RUN apt-get update && apt-get install -y nodejs npm

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy package.json and install Node dependencies
COPY package.json package-lock.json* ./
RUN npm install

# Copy source code
COPY . .

# Build React frontend
RUN npm run build

# Create non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 5000

# Start command
CMD ["python", "app.py"]