"""Per-instance configuration for a Security Gateway.

The SAME security-gateway software runs as multiple independent instances
(one per cluster). Every instance is identical and role-neutral: it can host
consumer applications and/or provider services. Values resolve via
common.settings: environment variable > variable_config.json > default, so a
Kubernetes ConfigMap can drive each Deployment without rebuilding the image.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common import settings

INSTANCE = settings.get("IM_INSTANCE", "general", "instance", "GOVSTACK")
GATEWAY_CODE = settings.get("SG_GATEWAY_CODE", "security_gateway", "gateway_code", "SG-DEFAULT")
DB_NAME = settings.get("SG_DB_NAME", "security_gateway", "db_name", "sgateway_db")

# Admin / app / UI port (plain HTTP) — browser dashboards + consumer application.
PORT = settings.get_int("SG_PORT", "security_gateway", "port", 8081)

# Mutual-TLS message port (HTTPS) — gateway-to-gateway traffic only. The ADDRESS
# registered in the global configuration is this mTLS endpoint.
MESSAGE_PORT = settings.get_int("SG_MESSAGE_PORT", "security_gateway", "message_port", 8443)
MTLS = settings.get_bool("SG_MTLS", "security_gateway", "mtls", True)
_default_addr = (f"https://127.0.0.1:{MESSAGE_PORT}" if MTLS
                 else f"http://127.0.0.1:{PORT}")
ADDRESS = settings.get("SG_ADDRESS", "security_gateway", "address", _default_addr)

# Certificate material on disk (written by bootstrap.py before uvicorn starts)
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_DIR = os.path.join(_ROOT, "certs", GATEWAY_CODE)
AUTH_CRT = os.path.join(CERT_DIR, "auth.crt")
AUTH_KEY = os.path.join(CERT_DIR, "auth.key")
CA_CRT = os.path.join(_ROOT, "certs", "ca.crt")

OWNER_CLASS = settings.get("SG_OWNER_CLASS", "security_gateway", "owner_class", "GOV")
OWNER_CODE = settings.get("SG_OWNER_CODE", "security_gateway", "owner_code", "0000")
OWNER_NAME = settings.get("SG_OWNER_NAME", "security_gateway", "owner_name", "Security Gateway Owner")
TITLE = settings.get("SG_TITLE", "security_gateway", "title", f"Security Gateway {GATEWAY_CODE}")

# When false (default), incoming subscription requests land as 'pending' and
# must be approved by the provider gateway administrator (X-Road access-rights
# model). Set to true to grant subscriptions automatically.
AUTO_APPROVE = settings.get_bool("SG_AUTO_APPROVE", "security_gateway", "auto_approve", False)
