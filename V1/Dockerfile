# Security Gateway image (independent). No database inside.
# Build FROM THE PROJECT ROOT (needs the shared common/ package):
#   docker build -f security_gateway/Dockerfile -t im-security-gateway .
#
# Config DEFAULTS ship in security_gateway/variable_config.json (SG1 values);
# override via env / ConfigMap (a second instance sets SG_GATEWAY_CODE=SG2 etc).
# One image, two run modes via SG_MODE (admin | mtls) - see docker-entrypoint.sh.
# Needs the CA + Global reachable (IM_CA_URL, IM_GLOBAL_URL). MySQL is external.
FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUTF8=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY common/           ./common/
COPY security_gateway/ ./security_gateway/
RUN chmod +x ./security_gateway/docker-entrypoint.sh

# admin port 8081, mtls message port 8443 (override via SG_PORT / SG_MESSAGE_PORT)
EXPOSE 8081 8443
ENTRYPOINT ["./security_gateway/docker-entrypoint.sh"]
