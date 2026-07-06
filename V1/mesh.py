"""Gateway-to-gateway HTTP(S) calls.

When the target URL is HTTPS (the registered mutual-TLS message endpoint of
another gateway), the request is made over **mutual TLS**: this gateway
presents its CA-issued auth certificate as the client certificate and verifies
the peer's server certificate against the CA. Plain-HTTP targets fall back to
ordinary requests (used when SG_MTLS is disabled).

Peer identity is verified two ways: (1) the certificate chains to the trusted
CA, and (2) the exact auth certificate is pinned in the signed global
configuration (`application_belongs_to_gateway`). Hostname verification is
therefore disabled, so gateways can be addressed by container/service DNS names
(Kubernetes, docker-compose) or IPs, not just localhost.
"""
import ssl

import httpx

from security_gateway import config

_ctx = None


def _client_context():
    global _ctx
    if _ctx is None:
        ctx = ssl.create_default_context(cafile=config.CA_CRT)
        ctx.check_hostname = False                     # identity pinned via global config + CA chain
        ctx.load_cert_chain(config.AUTH_CRT, config.AUTH_KEY)
        _ctx = ctx
    return _ctx


def post(url: str, json=None, timeout: int = 30):
    if config.MTLS and url.lower().startswith("https"):
        with httpx.Client(verify=_client_context(), timeout=timeout) as client:
            return client.post(url, json=json)
    return httpx.post(url, json=json, timeout=timeout)
