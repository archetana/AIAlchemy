# Multi-stage Dockerfile for FastAPI backend
# Optimized for production deployment on Google Cloud Run

# Stage 1: Build stage
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements-ultra-minimal.txt requirements.txt

# Install Python dependencies with verbose output for debugging
RUN echo "=== Upgrading pip ==="
RUN pip install --upgrade pip
RUN echo "=== Installing Python packages ==="
RUN pip install --no-cache-dir --verbose -r requirements.txt
RUN echo "=== Installation completed ==="

# Stage 2: Production stage
FROM python:3.11-slim as production

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.local/bin:$PATH"

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd -r aialchemy && useradd -r -g aialchemy aialchemy

# Set work directory and create necessary directories
WORKDIR /app
RUN mkdir -p /app/logs /app/uploads
RUN chown -R aialchemy:aialchemy /app

# Copy installed packages from builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=aialchemy:aialchemy . .

# Copy startup script
COPY startup.sh /app/startup.sh

RUN chmod +x /app/startup.sh
RUN chown aialchemy:aialchemy /app/startup.sh

# Switch to non-root user
USER aialchemy

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start application
CMD ["/app/startup.sh"]