FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install ffmpeg for audio processing
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create output directory with proper permissions
RUN mkdir -p output && chmod 777 output

# Ensure history.json can be created and modified
RUN touch output/history.json && chmod 666 output/history.json

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_DEBUG=0
ENV DOCKER_ENV=true
ENV PORT=5001

# Expose port
EXPOSE 5001

# Run the application
CMD ["python", "app.py"] 