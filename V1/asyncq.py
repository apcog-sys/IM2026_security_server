"""Async message queue operations (store-and-forward, consumer side)."""
import datetime as dt
import json

from security_gateway import models
from security_gateway.database import SessionLocal

MAX_ATTEMPTS = 6


def enqueue(message_id, consumer, service, body_obj, envelope, provider_address,
            callback_url=None):
    db = SessionLocal()
    try:
        db.add(models.AsyncMessage(
            message_id=message_id, direction="out", consumer=consumer, service=service,
            body=json.dumps(body_obj), envelope=json.dumps(envelope),
            provider_address=provider_address, callback_url=callback_url,
            status="queued", attempts=0, next_attempt=dt.datetime.utcnow()))
        db.commit()
    finally:
        db.close()


def due_batch(limit=20):
    """message_ids of queued messages whose retry time has arrived."""
    db = SessionLocal()
    try:
        now = dt.datetime.utcnow()
        rows = (db.query(models.AsyncMessage)
                .filter(models.AsyncMessage.status == "queued",
                        models.AsyncMessage.next_attempt <= now)
                .order_by(models.AsyncMessage.id).limit(limit).all())
        return [r.message_id for r in rows]
    finally:
        db.close()


def load(message_id):
    db = SessionLocal()
    try:
        r = db.query(models.AsyncMessage).filter_by(message_id=message_id).first()
        if not r:
            return None
        return {"message_id": r.message_id, "status": r.status, "attempts": r.attempts,
                "envelope": json.loads(r.envelope), "provider_address": r.provider_address,
                "callback_url": r.callback_url, "consumer": r.consumer, "service": r.service}
    finally:
        db.close()


def mark_completed(message_id, response):
    db = SessionLocal()
    try:
        r = db.query(models.AsyncMessage).filter_by(message_id=message_id).first()
        if r:
            r.status = "completed"
            r.response = json.dumps(response)
            r.error = None
            db.commit()
    finally:
        db.close()


def mark_retry_or_fail(message_id, error):
    """Bump the attempt count; schedule a backoff retry, or dead-letter."""
    db = SessionLocal()
    try:
        r = db.query(models.AsyncMessage).filter_by(message_id=message_id).first()
        if not r:
            return
        r.attempts += 1
        r.error = str(error)[:500]
        if r.attempts >= MAX_ATTEMPTS:
            r.status = "failed"
        else:
            backoff = min(60, 2 ** r.attempts)   # 2,4,8,16,32,60 seconds
            r.next_attempt = dt.datetime.utcnow() + dt.timedelta(seconds=backoff)
        db.commit()
    finally:
        db.close()


def mark_failed(message_id, error):
    """Permanent failure (e.g. a 4xx business rejection) — no retry."""
    db = SessionLocal()
    try:
        r = db.query(models.AsyncMessage).filter_by(message_id=message_id).first()
        if r:
            r.status = "failed"
            r.attempts += 1
            r.error = str(error)[:500]
            db.commit()
    finally:
        db.close()


def result(message_id):
    """Consumer polling view."""
    db = SessionLocal()
    try:
        r = db.query(models.AsyncMessage).filter_by(message_id=message_id).first()
        if not r:
            return None
        return {"message_id": r.message_id, "status": r.status, "attempts": r.attempts,
                "service": r.service,
                "response": json.loads(r.response) if r.response else None,
                "error": r.error,
                "created_at": r.created_at.isoformat() if r.created_at else None,
                "updated_at": r.updated_at.isoformat() if r.updated_at else None}
    finally:
        db.close()


def recent(limit=100):
    db = SessionLocal()
    try:
        rows = (db.query(models.AsyncMessage)
                .order_by(models.AsyncMessage.id.desc()).limit(limit).all())
        return [{"message_id": r.message_id, "consumer": r.consumer, "service": r.service,
                 "status": r.status, "attempts": r.attempts,
                 "callback_url": r.callback_url, "error": r.error,
                 "created_at": r.created_at.isoformat() if r.created_at else None}
                for r in rows]
    finally:
        db.close()
