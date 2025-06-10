# Certificate Generation System Docker Image
# Author: devag7 (Deva Garwalla)

FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

LABEL maintainer="devag7 (Dev Agarwalla)"
LABEL description="Professional Certificate Generator with Dynamic Content & QR Codes"
LABEL version="1.0"
LABEL author="devag7"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    imagemagick \
    redis-tools \
    curl \
    wget \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

# Configure ImageMagick to allow PDF processing
RUN sed -i 's/rights="none" pattern="PDF"/rights="read|write" pattern="PDF"/' /etc/ImageMagick-6/policy.xml

# Create app directory
WORKDIR /app

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create required directories
RUN mkdir -p certificates temp templates fonts logs pids

# Set permissions
RUN chmod +x setup.sh deploy.sh

# Create non-root user for security
RUN groupadd -r certgen && useradd -r -g certgen certgen
RUN chown -R certgen:certgen /app
USER certgen

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import redis; r=redis.Redis(host='redis', port=6379); r.ping()" || exit 1

# Expose ports
EXPOSE 5555

# Default command
CMD ["celery", "-A", "tasks", "worker", "--loglevel=info"]
