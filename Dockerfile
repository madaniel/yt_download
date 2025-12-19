FROM python:3.10-slim

WORKDIR /app

# Install system dependencies (ffmpeg for video processing)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY web_app.py ./
COPY cookies.txt ./

# Create downloads directory
RUN mkdir -p /downloads

EXPOSE 5000

CMD ["python", "web_app.py"]
