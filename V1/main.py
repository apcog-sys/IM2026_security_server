"""Security Gateway (Security Server equivalent).

Runs as multiple independent, IDENTICAL instances (one per cluster) from the
SAME code, parameterised only by env (instances/sg1.env, instances/sg2.env).
No instance is inherently a "consumer" or "provider" gateway — every instance
can do both; the role for a given message is decided by what is registered.

Each instance:
  * Owns an authentication identity (auth cert) and registers with the Global Server.
  * Hosts entity applications, each with a signing certificate.
  * Publishes services (registered locally AND in the global catalog).
  * Syncs the full service catalog from the Global Server (discovery).
  * Manages subscriptions: as a consumer (services it subscribes to) and as a
    provider (who is allowed to use its services).
  * Downloads + verifies the signed global configuration.
  * Mediates messages between gateways with signing, timestamping and logging.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from security_gateway import asyncq, config, database, messagelog, proxy, sg_core, worker
from security_gateway.database import SessionLocal
from security_gateway import models

app = FastAPI(title=config.TITLE, version="2.0")
worker.start(app)   # background async-delivery worker (gated by SG_RUN_WORKER)


class ApplicationReq(BaseModel):
    entity_class: str
    entity_code: str
    application_code: str
    entity_name: str = ""


class ServiceReq(BaseModel):
    entity_class: str
    entity_code: str
    application_code: str
    service_code: str
    backend_url: str
    description: str = ""


class SubscribeReq(BaseModel):
    application_id: str   # our hosted consumer application
    service_id: str       # remote service to subscribe to


class DecisionReq(BaseModel):
    service_code: str
    subscriber: str       # consumer application id


@app.on_event("startup")
def _startup():
    database.init()
    # Identity (auth cert) is always provisioned - the mutual-TLS port needs it.
    try:
        sg_core.provision_identity()
    except Exception as e:
        print(f"[{config.GATEWAY_CODE}] startup step 'identity' deferred: {e}")

    # In manual mode the operator performs registration / globalconf / catalog
    # by hand (POST /api/provision etc.). Otherwise do it automatically.
    if os.getenv("SG_MANUAL", "false").lower() in ("1", "true", "yes"):
        print(f"[{config.GATEWAY_CODE}] MANUAL mode: skipping auto register/globalconf/catalog")
        return
    for step, fn in [("register", sg_core.register_with_global),
                     ("globalconf", sg_core.refresh_globalconf),
                     ("catalog", sg_core.sync_catalog)]:
        try:
            fn()
        except Exception as e:
            print(f"[{config.GATEWAY_CODE}] startup step '{step}' deferred: {e}")


# ---- administration API ----
@app.post("/api/provision")
def provision():
    sg_core.register_with_global()
    out = sg_core.refresh_globalconf()
    sg_core.sync_catalog()
    return out


@app.post("/api/applications")
def add_application(r: ApplicationReq):
    return sg_core.add_application(r.entity_class, r.entity_code, r.application_code,
                                   r.entity_name)


@app.post("/api/services")
def add_service(r: ServiceReq):
    return sg_core.add_service(r.entity_class, r.entity_code, r.application_code,
                               r.service_code, r.backend_url, r.description)


@app.post("/api/subscribe")
def subscribe(r: SubscribeReq):
    try:
        return proxy.subscribe(r.application_id, r.service_id)
    except proxy.ProxyError as e:
        raise HTTPException(e.status, e.message)


@app.post("/api/subscribers/approve")
def approve_subscriber(r: DecisionReq):
    try:
        return proxy.set_subscription_decision(r.service_code, r.subscriber, "approved")
    except proxy.ProxyError as e:
        raise HTTPException(e.status, e.message)


@app.post("/api/subscribers/reject")
def reject_subscriber(r: DecisionReq):
    try:
        return proxy.set_subscription_decision(r.service_code, r.subscriber, "rejected")
    except proxy.ProxyError as e:
        raise HTTPException(e.status, e.message)


@app.post("/api/subscriptions/update")
async def subscriptions_update(request: Request):
    """Inbound: provider gateway pushes an approve/reject decision here."""
    body = await request.json()
    try:
        return proxy.receive_subscription_update(body)
    except proxy.ProxyError as e:
        return JSONResponse(status_code=e.status, content={"error": e.message})


@app.post("/api/globalconf/refresh")
def refresh():
    out = sg_core.refresh_globalconf()
    sg_core.sync_catalog()
    return out


@app.post("/api/catalog/refresh")
def catalog_refresh():
    return sg_core.sync_catalog()


# ---- discovery / status API ----
@app.get("/api/globalconf")
def get_conf():
    return sg_core.globalconf() or {}


@app.get("/api/catalog")
def catalog():
    return sg_core.list_catalog()


@app.get("/api/status")
def status():
    db = SessionLocal()
    try:
        ident = db.query(models.Identity).first()
        apps = [a.application_id for a in db.query(models.Application).all()]
    finally:
        db.close()
    conf = sg_core.globalconf() or {}
    return {"gateway_code": config.GATEWAY_CODE, "title": config.TITLE,
            "address": config.ADDRESS, "owner": f"{config.OWNER_CLASS}/{config.OWNER_CODE}",
            "registered": bool(ident and ident.registered),
            "auth_serial": ident.auth_serial if ident else None,
            "applications": apps, "globalconf_verified": conf.get("_verified", False)}


@app.get("/api/services")
def services():
    return sg_core.list_services()


@app.get("/api/subscribers")
def subscribers():
    return sg_core.list_subscribers()


@app.get("/api/subscriptions")
def subscriptions():
    return sg_core.list_subscriptions()


@app.get("/api/messagelog")
def msglog():
    return messagelog.recent()


# ---- update (PUT) API ----
class ServiceUpdate(BaseModel):
    backend_url: str | None = None
    description: str | None = None
    enabled: bool | None = None


@app.put("/api/services/{application_code}/{service_code}")
def update_service(application_code: str, service_code: str, r: ServiceUpdate):
    return sg_core.update_service(application_code, service_code,
                                  r.backend_url, r.description, r.enabled)


# ---- delete API (cascade=true removes dependent records) ----
@app.delete("/api/applications/{entity_class}/{entity_code}/{application_code}")
def delete_application(entity_class: str, entity_code: str, application_code: str,
                       cascade: bool = False):
    return sg_core.delete_application(entity_class, entity_code, application_code, cascade)


@app.delete("/api/services/{application_code}/{service_code}")
def delete_service(application_code: str, service_code: str):
    return sg_core.delete_service(application_code, service_code)


@app.delete("/api/subscribers")
def delete_subscriber(service_code: str, subscriber: str):
    return sg_core.delete_subscriber(service_code, subscriber)


@app.delete("/api/subscriptions")
def delete_subscription(application_id: str, service_id: str):
    return sg_core.delete_subscription(application_id, service_id)


@app.delete("/api/messagelog")
def clear_msglog():
    return sg_core.clear_message_log()


# ---- subscription handshake (gateway-to-gateway) ----
@app.post("/provider/subscribe")
async def provider_subscribe(request: Request):
    body = await request.json()
    try:
        return proxy.handle_incoming_subscription(body)
    except proxy.ProxyError as e:
        return JSONResponse(status_code=e.status, content={"error": e.message})


# ---- message mediation (synchronous) ----
@app.post("/consumer/request")
async def consumer_request(request: Request,
                           im_consumer: str = Header(...),
                           im_service: str = Header(...)):
    body = await request.json()
    try:
        return proxy.send(im_consumer, im_service, body)
    except proxy.ProxyError as e:
        raise HTTPException(e.status, e.message)


# ---- message mediation (asynchronous: submit + poll / callback) ----
@app.post("/consumer/request-async", status_code=202)
async def consumer_request_async(request: Request,
                                 im_consumer: str = Header(...),
                                 im_service: str = Header(...),
                                 im_callback: str = Header(default=None)):
    """Non-blocking: sign+timestamp+log now, queue for background delivery,
    return a receipt. Optional IM-Callback header = webhook to push the result."""
    body = await request.json()
    try:
        return proxy.submit_async(im_consumer, im_service, body, im_callback)
    except proxy.ProxyError as e:
        raise HTTPException(e.status, e.message)


@app.get("/consumer/messages/{message_id}")
def consumer_message(message_id: str):
    """Poll for an async message's status / result."""
    r = asyncq.result(message_id)
    if not r:
        raise HTTPException(404, "unknown message_id")
    return r


@app.get("/api/async-messages")
def async_messages():
    return asyncq.recent()


@app.post("/provider/receive")
async def provider_receive(request: Request):
    env = await request.json()
    try:
        return proxy.receive(env)
    except proxy.ProxyError as e:
        return JSONResponse(status_code=e.status, content={"error": e.message})


app.mount("/", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static"),
                           html=True), name="static")
