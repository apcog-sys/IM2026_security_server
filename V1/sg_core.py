"""Security Gateway core: identity, applications, services, global config,
service-catalog sync and subscriptions."""
import json

import httpx

from common import crypto
from common.topology import CA_URL, GLOBAL_URL, TSA_URL
from common.util import canonical_json
from security_gateway import config, models
from security_gateway.database import SessionLocal


# --------------------------------------------------------------------------
# Identity (auth certificate) + registration with the Global Server
# --------------------------------------------------------------------------

def provision_identity():
    db = SessionLocal()
    try:
        ident = db.query(models.Identity).first()
        if ident and ident.auth_cert_pem:
            return ident
        key = crypto.generate_rsa_key()
        cn = f"{config.GATEWAY_CODE} auth"
        csr = crypto.create_csr(key, cn, org=config.OWNER_NAME, org_unit="auth")
        data = httpx.post(f"{CA_URL}/api/sign",
                          json={"csr_pem": csr, "profile": crypto.PROFILE_AUTH,
                                "requested_by": config.GATEWAY_CODE}, timeout=15).json()
        ident = models.Identity(gateway_code=config.GATEWAY_CODE,
                                auth_cert_pem=data["cert_pem"],
                                auth_key_pem=crypto.key_to_pem(key),
                                auth_serial=data["serial"])
        db.add(ident)
        db.commit()
        db.refresh(ident)
        return ident
    finally:
        db.close()


def register_with_global():
    ident = provision_identity()
    httpx.post(f"{GLOBAL_URL}/api/gateways", json={
        "gateway_code": config.GATEWAY_CODE, "owner_class": config.OWNER_CLASS,
        "owner_code": config.OWNER_CODE, "address": config.ADDRESS,
        "auth_cert_pem": ident.auth_cert_pem}, timeout=15)
    db = SessionLocal()
    try:
        rec = db.query(models.Identity).first()
        rec.registered = True
        db.commit()
    finally:
        db.close()
    return {"ok": True}


# --------------------------------------------------------------------------
# Applications (hosted) — each gets an entity signing certificate, and is
# registered with the Global Server (entity + application + hosting).
# --------------------------------------------------------------------------

def add_application(entity_class, entity_code, application_code, entity_name=""):
    db = SessionLocal()
    try:
        existing = db.query(models.Application).filter_by(
            entity_class=entity_class, entity_code=entity_code,
            application_code=application_code).first()
        if existing and existing.sign_cert_pem:
            apprec = existing
        else:
            key = crypto.generate_rsa_key()
            cn = f"{entity_code}/{application_code} sign"
            csr = crypto.create_csr(key, cn, org=entity_name or entity_code,
                                    org_unit=application_code)
            data = httpx.post(f"{CA_URL}/api/sign",
                              json={"csr_pem": csr, "profile": crypto.PROFILE_SIGN,
                                    "requested_by": config.GATEWAY_CODE}, timeout=15).json()
            apprec = existing or models.Application(
                instance=config.INSTANCE, entity_class=entity_class,
                entity_code=entity_code, application_code=application_code)
            apprec.sign_cert_pem = data["cert_pem"]
            apprec.sign_key_pem = crypto.key_to_pem(key)
            apprec.sign_serial = data["serial"]
            if not existing:
                db.add(apprec)
            db.commit()
            db.refresh(apprec)

        # Register entity, application and hosting with the Global Server
        httpx.post(f"{GLOBAL_URL}/api/entities", json={
            "entity_class": entity_class, "entity_code": entity_code,
            "name": entity_name}, timeout=15)
        httpx.post(f"{GLOBAL_URL}/api/applications", json={
            "entity_class": entity_class, "entity_code": entity_code,
            "application_code": application_code}, timeout=15)
        httpx.post(f"{GLOBAL_URL}/api/gateway-applications", json={
            "gateway_code": config.GATEWAY_CODE, "entity_class": entity_class,
            "entity_code": entity_code, "application_code": application_code}, timeout=15)
        return {"ok": True, "application_id": apprec.application_id}
    finally:
        db.close()


def get_application(entity_class, entity_code, application_code):
    db = SessionLocal()
    try:
        return db.query(models.Application).filter_by(
            entity_class=entity_class, entity_code=entity_code,
            application_code=application_code).first()
    finally:
        db.close()


def get_hosted_application(application_id):
    parts = application_id.strip("/").split("/")
    if len(parts) != 4:
        return None
    return get_application(parts[1], parts[2], parts[3])


# --------------------------------------------------------------------------
# Services (provider role) — registered locally AND in the Global catalog.
# --------------------------------------------------------------------------

def add_service(entity_class, entity_code, application_code, service_code,
                backend_url, description=""):
    db = SessionLocal()
    try:
        rec = db.query(models.Service).filter_by(
            application_code=application_code, service_code=service_code).first()
        if rec:
            rec.backend_url, rec.description = backend_url, description
        else:
            rec = models.Service(entity_class=entity_class, entity_code=entity_code,
                                 application_code=application_code, service_code=service_code,
                                 backend_url=backend_url, description=description)
            db.add(rec)
        db.commit()
        db.refresh(rec)
        service_id = rec.service_id
    finally:
        db.close()

    # Publish to the Global Server service catalog
    httpx.post(f"{GLOBAL_URL}/api/services", json={
        "service_id": service_id, "gateway_code": config.GATEWAY_CODE,
        "description": description}, timeout=15)
    return {"ok": True, "service_id": service_id}


def find_service(application_code, service_code):
    db = SessionLocal()
    try:
        return db.query(models.Service).filter_by(
            application_code=application_code, service_code=service_code,
            enabled=True).first()
    finally:
        db.close()


def list_services():
    db = SessionLocal()
    try:
        out = []
        for s in db.query(models.Service).all():
            subs = [x.subscriber for x in db.query(models.Subscriber).filter_by(
                service_code=s.service_code, status="approved").all()]
            out.append({"service_id": s.service_id, "service_code": s.service_code,
                        "backend_url": s.backend_url, "description": s.description,
                        "enabled": s.enabled, "subscribers": subs})
        return out
    finally:
        db.close()


# --------------------------------------------------------------------------
# Subscriptions
# --------------------------------------------------------------------------

def add_subscriber(service_code, service_id, subscriber, status="approved"):
    """PROVIDER side: record that a consumer application may use our service."""
    db = SessionLocal()
    try:
        rec = db.query(models.Subscriber).filter_by(
            service_code=service_code, subscriber=subscriber).first()
        if rec:
            rec.status = status
        else:
            db.add(models.Subscriber(service_code=service_code, service_id=service_id,
                                     subscriber=subscriber, status=status))
        db.commit()
        return {"ok": True, "status": status}
    finally:
        db.close()


def add_subscription(application_id, service_id, provider_gateway, status="approved"):
    """CONSUMER side: record that our application subscribed to a service."""
    db = SessionLocal()
    try:
        rec = db.query(models.Subscription).filter_by(
            application_id=application_id, service_id=service_id).first()
        if rec:
            rec.status, rec.provider_gateway = status, provider_gateway
        else:
            db.add(models.Subscription(application_id=application_id, service_id=service_id,
                                       provider_gateway=provider_gateway, status=status))
        db.commit()
        return {"ok": True, "status": status}
    finally:
        db.close()


def is_subscribed(service_code, subscriber):
    """PROVIDER side authorization check (replaces the old ACL)."""
    db = SessionLocal()
    try:
        rec = db.query(models.Subscriber).filter_by(
            service_code=service_code, subscriber=subscriber, status="approved").first()
        return rec is not None
    finally:
        db.close()


def set_subscriber_status(service_code, subscriber, status):
    """PROVIDER side: approve/reject a pending subscription request."""
    db = SessionLocal()
    try:
        rec = db.query(models.Subscriber).filter_by(
            service_code=service_code, subscriber=subscriber).first()
        if not rec:
            return None
        rec.status = status
        db.commit()
        return {"service_id": rec.service_id, "subscriber": rec.subscriber,
                "service_code": rec.service_code, "status": rec.status}
    finally:
        db.close()


def update_subscription(application_id, service_id, status):
    """CONSUMER side: receive a status decision pushed by the provider gateway."""
    db = SessionLocal()
    try:
        rec = db.query(models.Subscription).filter_by(
            application_id=application_id, service_id=service_id).first()
        if rec:
            rec.status = status
            db.commit()
            return True
        return False
    finally:
        db.close()


def list_subscribers():
    db = SessionLocal()
    try:
        return [{"service_id": s.service_id, "service_code": s.service_code,
                 "subscriber": s.subscriber, "status": s.status}
                for s in db.query(models.Subscriber).all()]
    finally:
        db.close()


def list_subscriptions():
    db = SessionLocal()
    try:
        return [{"application_id": s.application_id, "service_id": s.service_id,
                 "provider_gateway": s.provider_gateway, "status": s.status}
                for s in db.query(models.Subscription).all()]
    finally:
        db.close()


# --------------------------------------------------------------------------
# Delete operations (with best-effort propagation to the Global Server)
# --------------------------------------------------------------------------

def delete_application(entity_class, entity_code, application_code, cascade=False):
    app_id = f"{config.INSTANCE}/{entity_class}/{entity_code}/{application_code}"
    db = SessionLocal()
    try:
        removed = 0
        if cascade:
            services = db.query(models.Service).filter_by(
                application_code=application_code).all()
            svc_ids = [s.service_id for s in services]
            svc_codes = [s.service_code for s in services]
            for s in services:
                db.delete(s)
                removed += 1
            for sub in db.query(models.Subscriber).all():
                if sub.service_code in svc_codes:
                    db.delete(sub)
                    removed += 1
            for sub in db.query(models.Subscription).all():
                if sub.application_id == app_id or sub.service_id in svc_ids:
                    db.delete(sub)
                    removed += 1
        removed += db.query(models.Application).filter_by(
            entity_class=entity_class, entity_code=entity_code,
            application_code=application_code).delete()
        db.commit()
    finally:
        db.close()
    # remove the hosting record + application (cascade) from the Global Server
    try:
        httpx.delete(f"{GLOBAL_URL}/api/gateway-applications/{config.GATEWAY_CODE}/"
                     f"{entity_class}/{entity_code}/{application_code}", timeout=15)
        httpx.delete(f"{GLOBAL_URL}/api/applications/{entity_class}/{entity_code}/"
                     f"{application_code}", params={"cascade": str(cascade).lower()},
                     timeout=15)
    except Exception:
        pass
    return {"deleted": removed, "cascade": cascade}


def update_service(application_code, service_code, backend_url=None,
                   description=None, enabled=None):
    db = SessionLocal()
    try:
        rec = db.query(models.Service).filter_by(
            application_code=application_code, service_code=service_code).first()
        if not rec:
            return {"updated": 0}
        if backend_url is not None:
            rec.backend_url = backend_url
        if description is not None:
            rec.description = description
        if enabled is not None:
            rec.enabled = enabled
        db.commit()
        service_id, desc = rec.service_id, rec.description
    finally:
        db.close()
    # keep the Global catalog description in sync
    try:
        httpx.post(f"{GLOBAL_URL}/api/services",
                   json={"service_id": service_id, "gateway_code": config.GATEWAY_CODE,
                         "description": desc}, timeout=15)
    except Exception:
        pass
    return {"updated": 1, "service_id": service_id}


def delete_service(application_code, service_code):
    db = SessionLocal()
    try:
        rec = db.query(models.Service).filter_by(
            application_code=application_code, service_code=service_code).first()
        service_id = rec.service_id if rec else None
        n = db.query(models.Service).filter_by(
            application_code=application_code, service_code=service_code).delete()
        db.commit()
    finally:
        db.close()
    if service_id:                       # remove from the Global catalog too
        try:
            httpx.delete(f"{GLOBAL_URL}/api/services",
                         params={"service_id": service_id}, timeout=15)
        except Exception:
            pass
    return {"deleted": n, "service_id": service_id}


def delete_subscriber(service_code, subscriber):
    """PROVIDER side: revoke a granted subscription."""
    db = SessionLocal()
    try:
        rec = db.query(models.Subscriber).filter_by(
            service_code=service_code, subscriber=subscriber).first()
        service_id = rec.service_id if rec else None
        n = db.query(models.Subscriber).filter_by(
            service_code=service_code, subscriber=subscriber).delete()
        db.commit()
    finally:
        db.close()
    if service_id:
        try:
            httpx.delete(f"{GLOBAL_URL}/api/subscriptions",
                         params={"subscriber": subscriber, "service_id": service_id},
                         timeout=15)
        except Exception:
            pass
    return {"deleted": n}


def delete_subscription(application_id, service_id):
    """CONSUMER side: drop a subscription our application holds."""
    db = SessionLocal()
    try:
        n = db.query(models.Subscription).filter_by(
            application_id=application_id, service_id=service_id).delete()
        db.commit()
    finally:
        db.close()
    try:
        httpx.delete(f"{GLOBAL_URL}/api/subscriptions",
                     params={"subscriber": application_id, "service_id": service_id},
                     timeout=15)
    except Exception:
        pass
    return {"deleted": n}


def clear_message_log():
    db = SessionLocal()
    try:
        n = db.query(models.MessageLog).delete()
        db.commit()
        return {"deleted": n}
    finally:
        db.close()


# --------------------------------------------------------------------------
# Global configuration: fetch, verify against anchor, cache, query
# --------------------------------------------------------------------------

def refresh_globalconf():
    signed = httpx.get(f"{GLOBAL_URL}/api/globalconf", timeout=15).json()
    anchor = httpx.get(f"{GLOBAL_URL}/api/anchor", timeout=15).json()
    signer_cert = crypto.load_cert(signed["signer_cert_pem"])
    ca_cert = crypto.load_cert(anchor["ca_cert_pem"])
    chain_ok = crypto.verify_cert_chain(signer_cert, ca_cert)
    sig_ok = crypto.verify_bytes(canonical_json(signed["conf"]),
                                 signed["signature"], signer_cert)
    verified = chain_ok and sig_ok

    db = SessionLocal()
    try:
        db.query(models.GlobalConfCache).delete()
        db.add(models.GlobalConfCache(
            conf_json=json.dumps(signed["conf"]), signature=signed["signature"],
            signer_cert_pem=signed["signer_cert_pem"], verified=verified))
        db.commit()
    finally:
        db.close()
    return {"verified": verified, "chain_ok": chain_ok, "sig_ok": sig_ok}


def globalconf():
    db = SessionLocal()
    try:
        rec = db.query(models.GlobalConfCache).order_by(
            models.GlobalConfCache.id.desc()).first()
        if not rec:
            return None
        conf = json.loads(rec.conf_json)
        conf["_verified"] = rec.verified
        return conf
    finally:
        db.close()


# --------------------------------------------------------------------------
# Service catalog sync (from Global Server)
# --------------------------------------------------------------------------

def sync_catalog():
    services = httpx.get(f"{GLOBAL_URL}/api/services", timeout=15).json()
    db = SessionLocal()
    try:
        db.query(models.ServiceCatalog).delete()
        for s in services:
            db.add(models.ServiceCatalog(service_id=s["service_id"],
                                         gateway_code=s["gateway_code"],
                                         description=s.get("description", "")))
        db.commit()
    finally:
        db.close()
    return {"ok": True, "count": len(services)}


def list_catalog():
    db = SessionLocal()
    try:
        return [{"service_id": s.service_id, "gateway_code": s.gateway_code,
                 "description": s.description}
                for s in db.query(models.ServiceCatalog).order_by(
                    models.ServiceCatalog.service_id).all()]
    finally:
        db.close()


# --------------------------------------------------------------------------
# Trust / topology lookups using the verified global configuration
# --------------------------------------------------------------------------

def trusted_ca_certs(conf=None):
    conf = conf or globalconf() or {}
    return [crypto.load_cert(p) for p in conf.get("trusted_cas", [])]


def find_provider_gateway(provider_application_id, conf=None):
    conf = conf or globalconf() or {}
    for gw in conf.get("security_gateways", []):
        if provider_application_id in gw.get("applications", []):
            return gw
    return None


def find_gateway_for_service(service_id, conf=None):
    conf = conf or globalconf() or {}
    for s in conf.get("services", []):
        if s.get("service_id") == service_id:
            for gw in conf.get("security_gateways", []):
                if gw.get("gateway_code") == s.get("gateway_code"):
                    return gw
    return None


def application_belongs_to_gateway(application_id, auth_cert_pem, conf=None):
    conf = conf or globalconf() or {}
    for gw in conf.get("security_gateways", []):
        if gw.get("auth_cert_pem", "").strip() == auth_cert_pem.strip():
            return application_id in gw.get("applications", [])
    return False


def cert_trusted(cert_pem, conf=None):
    try:
        cert = crypto.load_cert(cert_pem)
    except Exception:
        return False
    chained = any(crypto.verify_cert_chain(cert, ca) for ca in trusted_ca_certs(conf))
    if not chained:
        return False
    try:
        r = httpx.get(f"{CA_URL}/api/ocsp/{crypto.cert_serial(cert)}", timeout=10).json()
        return r.get("status") == "good"
    except Exception:
        return True  # OCSP unreachable -> soft-fail (cert already chain-valid)


def tsa_url(conf=None):
    conf = conf or globalconf() or {}
    tsas = conf.get("trusted_tsas", [])
    return tsas[0]["url"] if tsas else TSA_URL
