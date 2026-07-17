#!/bin/sh
# Security Gateway entrypoint. One image, two run modes (SG_MODE):
#   admin  (default) - HTTP admin/app/UI port; bootstraps the auth cert.
#   mtls             - HTTPS mutual-TLS message port; waits for the shared cert.
# Run the two modes as two containers of the same pod, sharing a /app/certs volume.
set -e
: "${SG_MODE:=admin}"

if [ "$SG_MODE" = "mtls" ]; then
  CERT="/app/certs/${SG_GATEWAY_CODE}/auth.crt"
  echo "gateway(mtls): waiting for ${CERT} (bootstrapped by the admin container) ..."
  while [ ! -f "$CERT" ]; do sleep 1; done
  exec uvicorn security_gateway.main:app --host 0.0.0.0 --port "${SG_MESSAGE_PORT:-8443}" \
    --ssl-keyfile  "/app/certs/${SG_GATEWAY_CODE}/auth.key" \
    --ssl-certfile "/app/certs/${SG_GATEWAY_CODE}/auth.crt" \
    --ssl-ca-certs "/app/certs/ca.crt" \
    --ssl-cert-reqs 2
else
  python -m security_gateway.bootstrap      # obtain auth cert from the CA -> /app/certs
  exec uvicorn security_gateway.main:app --host 0.0.0.0 --port "${SG_PORT:-8081}"
fi
