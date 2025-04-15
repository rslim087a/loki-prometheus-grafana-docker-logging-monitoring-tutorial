FROM python:3.9-slim

WORKDIR /app

# Install required package
RUN pip install --no-cache-dir prometheus-client

# Copy the script
COPY log_to_metrics.py .

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Expose the metrics port
EXPOSE 8082

# Run the script
CMD ["python", "log_to_metrics.py"]