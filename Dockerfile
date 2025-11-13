# Dockerfile for Model Training Application
# Multi-stage build for optimized image size

# Stage 1: Base image with Python and system dependencies
FROM nvidia/cuda:12.1.0-cudnn8-devel-ubuntu22.04 AS base

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    python3-dev \
    git \
    wget \
    curl \
    build-essential \
    libssl-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Create symbolic link for python
RUN ln -s /usr/bin/python3.10 /usr/bin/python

# Upgrade pip
RUN pip install --upgrade pip setuptools wheel

# Stage 2: Dependencies
FROM base AS dependencies

# Set working directory
WORKDIR /app

# Copy requirements files
COPY requirements.txt requirements-dev.txt* ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install development dependencies if available
RUN if [ -f requirements-dev.txt ]; then \
        pip install --no-cache-dir -r requirements-dev.txt; \
    fi

# Stage 3: Application
FROM dependencies AS application

# Set working directory
WORKDIR /app

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p datasets models logs

# Set Python path
ENV PYTHONPATH=/app:$PYTHONPATH

# Expose ports
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Stage 4: Development image (optional)
FROM application AS development

# Install additional development tools
RUN pip install --no-cache-dir \
    ipython \
    jupyter \
    notebook

# Enable hot reloading for development
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
