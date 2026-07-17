"""Non-repudiation message log."""
from security_gateway import models
from security_gateway.database import SessionLocal


def log(message_id, direction, consumer, service, request_hash, signature,
        sig_verified=False, ts_serial=None, ts_verified=False,
        response_status=None, note=""):
    db = SessionLocal()
    try:
        db.add(models.MessageLog(
            message_id=message_id, direction=direction, consumer=consumer, service=service,
            request_hash=request_hash, signature=signature, sig_verified=sig_verified,
            ts_serial=ts_serial, ts_verified=ts_verified,
            response_status=response_status, note=note[:500]))
        db.commit()
    finally:
        db.close()


def recent(limit=100):
    db = SessionLocal()
    try:
        rows = (db.query(models.MessageLog)
                .order_by(models.MessageLog.id.desc()).limit(limit).all())
        return [{"message_id": r.message_id, "direction": r.direction,
                 "consumer": r.consumer, "service": r.service,
                 "request_hash": (r.request_hash or "")[:20],
                 "sig_verified": r.sig_verified, "ts_serial": (r.ts_serial or "")[:12],
                 "ts_verified": r.ts_verified, "response_status": r.response_status,
                 "note": r.note,
                 "created_at": r.created_at.isoformat() if r.created_at else None}
                for r in rows]
    finally:
        db.close()
