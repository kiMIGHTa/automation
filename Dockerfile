# Use official Python image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /automation

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY automation.py populate_db.py ./
COPY config.json ./

# Create output directory for exports
RUN mkdir -p /root/Downloads/BusinessExports

# Expose any ports if needed (not required for this script)
# EXPOSE 8000

# Run database population on build (optional, or run at container start)
RUN python populate_db.py

# Create a non-root user
RUN useradd -m appuser

# Change ownership of the working directory and output directory
RUN chown -R appuser:appuser /automation /root/Downloads/BusinessExports

# Switch to the non-root user
USER appuser

# Set default command to run the automation script
CMD ["python", "automation.py"]