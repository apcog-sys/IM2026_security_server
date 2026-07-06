"""Message mediation + subscription orchestration between gateways.

Consumer side (send):  enforce subscription, sign + timestamp + log, forward
                       to the provider gateway.
Provider side (receive): authenticate sender, verify signature + timestamp,
                       enforce subscription, forward to backend, sign response.
"""
import uuid

import httpx

from common import crypto, xroad
from common.util import canonical_json
from security_gateway import asyncq, config, mesh, messagelog, models, sg_core
from security_gateway.database import SessionLocal


class ProxyError(Exception):
    def __init__(self, status, message):
        super().__init__(message)
        self.status = status
        self.message = message


def _identity():
    db = SessionLocal()
    try:
        return db.query(models.Identity).first()
    finally:
        db.close()


# --------------------------------------------------------------------------
# Subscription orchestration
# --------------------------------------------------------------------------

def subscribe(application_id_str: str, service_id_str: str) -> dict:
    """CONSUMER side: subscribe one of our applications to a remote service."""
    app = xroad.ApplicationId.parse(application_id_str)
    service = xroad.ServiceId.parse(service_id_str)

    hosted = sg_core.get_application(app.entity_class, app.entity_code, app.application)
    if not hosted:
        raise ProxyError(403, f"application {application_id_str} is not hosted here")

    conf = sg_core.globalconf()
    if not conf:
        raise ProxyError(503, "global configuration not available")

    provider_gw = (sg_core.find_gateway_for_service(service_id_str, conf)
                   or sg_core.find_provider_gateway(str(service.provider), conf))
    if not provider_gw:
        raise ProxyError(404, f"no gateway publishes service {service_id_str}")

    # Ask the provider gateway to authorise the subscription (over mutual TLS)
    try:
        r = mesh.post(f"{provider_gw['address']}/provider/subscribe",
                      json={"subscriber": application_id_str,
                            "service_id": service_id_str,
                            "service_code": service.service_code,
                            "auth_cert_pem": _identity().auth_cert_pem}, timeout=20)
    except Exception as e:
        raise ProxyError(502, f"provider gateway unreachable: {e}")
    if r.status_code >= 400:
        raise ProxyError(r.status_code, f"subscription rejected: {r.text}")
    status = r.json().get("status", "approved")

    # Record on the consumer side + centrally in the Global Server
    sg_core.add_subscription(application_id_str, service_id_str,
                             provider_gw["gateway_code"], status)
    from common.topology import GLOBAL_URL
    httpx.post(f"{GLOBAL_URL}/api/subscriptions",
               json={"subscriber": application_id_str, "service_id": service_id_str,
                     "status": status}, timeout=15)
    return {"ok": True, "status": status, "provider_gateway": provider_gw["gateway_code"]}


def handle_incoming_subscription(body: dict) -> dict:
    """PROVIDER side: record a subscription request (pending unless auto-approve)."""
    subscriber = body.get("subscriber", "")
    service_id = body.get("service_id", "")
    service_code = body.get("service_code", "")
    conf = sg_core.globalconf() or {}

    # The requesting gateway must be authenticated
    auth_cert_pem = body.get("auth_cert_pem", "")
    if auth_cert_pem and not sg_core.cert_trusted(auth_cert_pem, conf):
        raise ProxyError(401, "requesting gateway is not trusted")

    service = xroad.ServiceId.parse(service_id)
    svc = sg_core.find_service(service.application, service.service_code)
    if not svc:
        raise ProxyError(404, f"service {service_code} not published here")

    status = "approved" if config.AUTO_APPROVE else "pending"
    sg_core.add_subscriber(service_code, service_id, subscriber, status=status)
    return {"status": status, "service_id": service_id, "subscriber": subscriber}


def set_subscription_decision(service_code: str, subscriber: str, decision: str) -> dict:
    """PROVIDER side admin action: approve/reject a subscription request, then
    propagate the decision back to the consumer gateway and the Global Server."""
    rec = sg_core.set_subscriber_status(service_code, subscriber, decision)
    if not rec:
        raise ProxyError(404, f"no subscription request for {subscriber} -> {service_code}")
    service_id = rec["service_id"]

    # Propagate to the consumer gateway that hosts the subscriber application
    conf = sg_core.globalconf() or {}
    consumer_gw = sg_core.find_provider_gateway(subscriber, conf)  # gateway hosting subscriber
    if consumer_gw:
        try:
            mesh.post(f"{consumer_gw['address']}/api/subscriptions/update",
                      json={"application_id": subscriber, "service_id": service_id,
                            "status": decision,
                            "auth_cert_pem": _identity().auth_cert_pem}, timeout=15)
        except Exception:
            pass

    # Propagate to the Global Server central record
    from common.topology import GLOBAL_URL
    try:
        httpx.post(f"{GLOBAL_URL}/api/subscriptions",
                   json={"subscriber": subscriber, "service_id": service_id,
                         "status": decision}, timeout=15)
    except Exception:
        pass
    return {"ok": True, "status": decision, "service_id": service_id, "subscriber": subscriber}


def receive_subscription_update(body: dict) -> dict:
    """CONSUMER side: accept a status decision pushed by the provider gateway."""
    auth_cert_pem = body.get("auth_cert_pem", "")
    conf = sg_core.globalconf() or {}
    if auth_cert_pem and not sg_core.cert_trusted(auth_cert_pem, conf):
        raise ProxyError(401, "updating gateway is not trusted")
    sg_core.update_subscription(body["application_id"], body["service_id"],
                                body.get("status", "approved"))
    return {"ok": True}


# --------------------------------------------------------------------------
# Consumer side: send a request
# --------------------------------------------------------------------------

def _prepare(consumer_id_str: str, service_id_str: str, body_obj) -> dict:
    """Validate + subscription-gate + build a signed, timestamped, logged
    envelope ready to POST to the provider gateway. Shared by the synchronous
    send() and the asynchronous submit path (identical non-repudiation)."""
    consumer = xroad.ApplicationId.parse(consumer_id_str)
    service = xroad.ServiceId.parse(service_id_str)

    hosted = sg_core.get_application(consumer.entity_class, consumer.entity_code,
                                     consumer.application)
    if not hosted:
        raise ProxyError(403, f"application {consumer_id_str} is not hosted here")

    # Consumer-side subscription gate (must subscribe before consuming)
    if not _has_subscription(consumer_id_str, service_id_str):
        raise ProxyError(403, f"{consumer_id_str} is not subscribed to {service_id_str}")

    conf = sg_core.globalconf()
    if not conf:
        raise ProxyError(503, "global configuration not available")

    provider_gw = (sg_core.find_gateway_for_service(service_id_str, conf)
                   or sg_core.find_provider_gateway(str(service.provider), conf))
    if not provider_gw:
        raise ProxyError(404, f"no gateway publishes service {service_id_str}")

    message_id = uuid.uuid4().hex
    body_bytes = canonical_json(body_obj)
    canonical = xroad.canonical_message(message_id, str(consumer), str(service), body_bytes)
    signature = crypto.sign_bytes(canonical, crypto.load_key(hosted.sign_key_pem))
    imprint = crypto.sha256_b64(canonical)
    ts_token, ts_serial, ts_ok = _timestamp(imprint, conf)

    ident = _identity()
    envelope = {
        "message_id": message_id, "consumer": str(consumer), "service": str(service),
        "body": body_obj, "signature": signature, "sign_cert_pem": hosted.sign_cert_pem,
        "auth_cert_pem": ident.auth_cert_pem, "ts_token": ts_token,
    }
    return {"message_id": message_id, "consumer": str(consumer), "service": str(service),
            "provider_gw": provider_gw, "envelope": envelope,
            "imprint": imprint, "ts_serial": ts_serial, "ts_ok": ts_ok}


def _format_result(p: dict, out: dict) -> dict:
    return {
        "im": {"message_id": p["message_id"], "request_timestamp_serial": p["ts_serial"],
               "request_timestamped": p["ts_ok"],
               "provider_response_signed": bool(out.get("provider_signature")),
               "provider_response_ts_serial": out.get("provider_ts_serial")},
        "status": out.get("status"), "body": out.get("body"),
    }


def send(consumer_id_str: str, service_id_str: str, body_obj) -> dict:
    """Synchronous mediation: build + deliver + wait for the response."""
    p = _prepare(consumer_id_str, service_id_str, body_obj)
    messagelog.log(p["message_id"], "out", p["consumer"], p["service"], p["imprint"],
                   p["envelope"]["signature"], sig_verified=True, ts_serial=p["ts_serial"],
                   ts_verified=p["ts_ok"], note=f"-> {p['provider_gw']['address']}")
    try:
        resp = mesh.post(f"{p['provider_gw']['address']}/provider/receive",
                         json=p["envelope"], timeout=30)
    except Exception as e:
        raise ProxyError(502, f"provider gateway unreachable: {e}")
    if resp.status_code >= 400:
        raise ProxyError(resp.status_code, f"provider rejected: {resp.text}")

    out = resp.json()
    messagelog.log(p["message_id"], "out", p["consumer"], p["service"], p["imprint"],
                   p["envelope"]["signature"], sig_verified=True, ts_serial=p["ts_serial"],
                   ts_verified=p["ts_ok"], response_status=out.get("status"),
                   note="response received")
    return _format_result(p, out)


# --------------------------------------------------------------------------
# Consumer side: ASYNCHRONOUS (store-and-forward) — non-blocking submit,
# background delivery with retries, poll or callback for the result.
# The synchronous send() above is untouched.
# --------------------------------------------------------------------------

def submit_async(consumer_id_str: str, service_id_str: str, body_obj,
                 callback_url: str = None) -> dict:
    """Sign + timestamp + log now, enqueue, return immediately (202-style)."""
    p = _prepare(consumer_id_str, service_id_str, body_obj)
    messagelog.log(p["message_id"], "out", p["consumer"], p["service"], p["imprint"],
                   p["envelope"]["signature"], sig_verified=True, ts_serial=p["ts_serial"],
                   ts_verified=p["ts_ok"], note=f"queued (async) -> {p['provider_gw']['address']}")
    asyncq.enqueue(p["message_id"], p["consumer"], p["service"], body_obj, p["envelope"],
                   p["provider_gw"]["address"], callback_url)
    return {"message_id": p["message_id"], "status": "queued",
            "request_timestamp_serial": p["ts_serial"], "request_timestamped": p["ts_ok"]}


def deliver_one(message_id: str) -> None:
    """Deliver one queued message to the provider gateway (called by the worker
    in a thread). Retries on transport/5xx errors; dead-letters 4xx rejections."""
    m = asyncq.load(message_id)
    if not m or m["status"] != "queued":
        return
    try:
        resp = mesh.post(f"{m['provider_address']}/provider/receive",
                         json=m["envelope"], timeout=30)
    except Exception as e:
        asyncq.mark_retry_or_fail(message_id, f"provider unreachable: {e}")
        return
    if resp.status_code >= 500:
        asyncq.mark_retry_or_fail(message_id, f"provider {resp.status_code}: {resp.text[:200]}")
        return
    if resp.status_code >= 400:                       # business rejection -> permanent
        asyncq.mark_failed(message_id, f"provider {resp.status_code}: {resp.text[:200]}")
        return
    out = resp.json()
    asyncq.mark_completed(message_id, out)
    messagelog.log(message_id, "out", m["consumer"], m["service"], "",
                   m["envelope"].get("signature", ""), sig_verified=True,
                   response_status=out.get("status"), note="async response received")
    if m.get("callback_url"):
        try:
            import httpx
            httpx.post(m["callback_url"],
                       json={"message_id": message_id, "result": out}, timeout=15)
        except Exception:
            pass


def _has_subscription(application_id, service_id):
    db = SessionLocal()
    try:
        return db.query(models.Subscription).filter_by(
            application_id=application_id, service_id=service_id,
            status="approved").first() is not None
    finally:
        db.close()


# --------------------------------------------------------------------------
# Provider side: receive a request
# --------------------------------------------------------------------------

def receive(env: dict) -> dict:
    conf = sg_core.globalconf()
    if not conf:
        raise ProxyError(503, "global configuration not available")

    message_id = env.get("message_id", "")
    consumer_str = env["consumer"]
    service_str = env["service"]
    body_obj = env.get("body")
    signature = env.get("signature", "")
    sign_cert_pem = env.get("sign_cert_pem", "")
    auth_cert_pem = env.get("auth_cert_pem", "")
    ts_token = env.get("ts_token")

    service = xroad.ServiceId.parse(service_str)

    # 1) Authenticate the sending gateway + origin binding
    if not sg_core.cert_trusted(auth_cert_pem, conf):
        raise ProxyError(401, "sender authentication certificate is not trusted")
    if not sg_core.application_belongs_to_gateway(consumer_str, auth_cert_pem, conf):
        raise ProxyError(401, f"application {consumer_str} is not hosted on the sending gateway")

    # 2) Verify the message signature
    if not sg_core.cert_trusted(sign_cert_pem, conf):
        raise ProxyError(401, "message signing certificate is not trusted")
    body_bytes = canonical_json(body_obj)
    canonical = xroad.canonical_message(message_id, consumer_str, service_str, body_bytes)
    sign_cert = crypto.load_cert(sign_cert_pem)
    sig_ok = crypto.verify_bytes(canonical, signature, sign_cert)
    if not sig_ok:
        raise ProxyError(401, "message signature verification failed")

    # 3) Verify the timestamp
    imprint = crypto.sha256_b64(canonical)
    ts_ok, ts_serial = _verify_timestamp(ts_token, imprint, conf)

    # 4) Subscription check (authorization)
    if not sg_core.is_subscribed(service.service_code, consumer_str):
        raise ProxyError(403, f"no active subscription: {consumer_str} -> {service.service_code}")

    # 5) Resolve and call the backend service
    svc = sg_core.find_service(service.application, service.service_code)
    if not svc:
        raise ProxyError(404, f"service {service.service_code} not found on this gateway")
    try:
        backend = httpx.post(svc.backend_url, json=body_obj, timeout=30)
        backend_status = backend.status_code
        try:
            backend_body = backend.json()
        except Exception:
            backend_body = {"raw": backend.text}
    except Exception as e:
        raise ProxyError(502, f"backend service unreachable: {e}")

    messagelog.log(message_id, "in", consumer_str, service_str, imprint, signature,
                   sig_verified=sig_ok, ts_serial=ts_serial, ts_verified=ts_ok,
                   response_status=backend_status,
                   note=f"subscription ok; backend {svc.backend_url}")

    # 6) Sign + timestamp the response
    provider_sig = None
    provider_ts_serial = None
    prov = sg_core.get_application(service.entity_class, service.entity_code,
                                   service.application)
    if prov and prov.sign_key_pem:
        resp_bytes = canonical_json(backend_body)
        resp_canonical = xroad.canonical_message(message_id, service_str, consumer_str,
                                                 resp_bytes)
        provider_sig = crypto.sign_bytes(resp_canonical, crypto.load_key(prov.sign_key_pem))
        _, provider_ts_serial, _ = _timestamp(crypto.sha256_b64(resp_canonical), conf)

    return {
        "status": backend_status, "body": backend_body, "message_id": message_id,
        "checks": {"sender_authenticated": True, "signature_verified": sig_ok,
                   "timestamp_verified": ts_ok, "subscription": "active"},
        "provider_signature": provider_sig,
        "provider_sign_cert_pem": prov.sign_cert_pem if prov else None,
        "provider_ts_serial": provider_ts_serial,
    }


# --------------------------------------------------------------------------
# Timestamp helpers
# --------------------------------------------------------------------------

def _timestamp(imprint_b64: str, conf):
    try:
        token = httpx.post(f"{sg_core.tsa_url(conf)}/api/timestamp",
                           json={"hashed_message": imprint_b64,
                                 "requester": config.GATEWAY_CODE}, timeout=15).json()
        return token, token["tst_info"]["serial_number"], True
    except Exception:
        return None, None, False


def _verify_timestamp(token, expected_imprint, conf):
    if not token:
        return False, None
    try:
        serial = token["tst_info"]["serial_number"]
        if token["tst_info"]["message_imprint"]["hashed_message"] != expected_imprint:
            return False, serial
        tsa_cert = crypto.load_cert(token["tsa_cert_pem"])
        if not any(crypto.verify_cert_chain(tsa_cert, ca)
                   for ca in sg_core.trusted_ca_certs(conf)):
            return False, serial
        ok = crypto.verify_bytes(canonical_json(token["tst_info"]),
                                 token["signature"], tsa_cert)
        return ok, serial
    except Exception:
        return False, None
