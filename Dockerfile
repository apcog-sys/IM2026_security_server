FROM python:3.10-slim

WORKDIR /app

# Install dependencies first (layer cached separately from source)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY ss1.py .
COPY certificate_generation.py .
COPY index.html .

# Directory for generated certificates (mount as a volume to persist across restarts)
RUN mkdir -p /app/certificates

# db_config.json is NOT baked in — mount it at runtime:
#   docker run -v ./db_config.json:/app/db_config.json ...
# Or configure the DB connection via the UI after the container starts.

EXPOSE 8000

# PORT and HOST can be overridden at runtime:
#   docker run ... -e PORT=9000
ENV PORT=8000
ENV HOST=0.0.0.0

CMD ["sh", "-c", "python ss1.py --port $PORT --host $HOST"]
