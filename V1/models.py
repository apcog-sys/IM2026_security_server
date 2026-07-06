import datetime as dt

from sqlalchemy import (Column, DateTime, Integer, String, Text, Boolean,
                        UniqueConstraint)

from security_gateway.database import Base


class Identity(Base):
    """The security gateway's own authentication identity."""
    __tablename__ = "sg_identity"
    id = Column(Integer, primary_key=True)
    gateway_code = Column(String(64))
    auth_cert_pem = Column(Text)
    auth_key_pem = Column(Text)
    auth_serial = Column(String(64))
    registered = Column(Boolean, default=False)
    created_at = Column(DateTime, default=dt.datetime.utcnow)


class Application(Base):
    """An entity application hosted on this gateway (consumer and/or provider)."""
    __tablename__ = "sg_application"
    id = Column(Integer, primary_key=True)
    instance = Column(String(32))
    entity_class = Column(String(32))
    entity_code = Column(String(64))
    application_code = Column(String(64))
    sign_cert_pem = Column(Text)
    sign_key_pem = Column(Text)
    sign_serial = Column(String(64))
    created_at = Column(DateTime, default=dt.datetime.utcnow)
    __table_args__ = (UniqueConstraint("entity_class", "entity_code", "application_code"),)

    @property
    def application_id(self):
        return f"{self.instance}/{self.entity_class}/{self.entity_code}/{self.application_code}"


class Service(Base):
    """A REST service published by a provider application on this gateway."""
    __tablename__ = "sg_service"
    id = Column(Integer, primary_key=True)
    entity_class = Column(String(32))
    entity_code = Column(String(64))
    application_code = Column(String(64))
    service_code = Column(String(64))
    backend_url = Column(String(512))
    description = Column(String(255))
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=dt.datetime.utcnow)

    @property
    def service_id(self):
        from security_gateway import config
        return f"{config.INSTANCE}/{self.entity_class}/{self.entity_code}/{self.application_code}/{self.service_code}"


class Subscriber(Base):
    """PROVIDER side: a consumer application authorised to use one of our services.
    (who uses what — the access right granted by a subscription)."""
    __tablename__ = "sg_subscriber"
    id = Column(Integer, primary_key=True)
    service_code = Column(String(64))
    service_id = Column(String(255))
    subscriber = Column(String(255))   # consumer application id
    status = Column(String(16), default="approved")
    created_at = Column(DateTime, default=dt.datetime.utcnow)
    __table_args__ = (UniqueConstraint("service_code", "subscriber"),)


class Subscription(Base):
    """CONSUMER side: a service one of our applications has subscribed to."""
    __tablename__ = "sg_subscription"
    id = Column(Integer, primary_key=True)
    application_id = Column(String(255))   # our consumer application id
    service_id = Column(String(255))
    provider_gateway = Column(String(64))
    status = Column(String(16), default="approved")
    created_at = Column(DateTime, default=dt.datetime.utcnow)
    __table_args__ = (UniqueConstraint("application_id", "service_id"),)


class ServiceCatalog(Base):
    """Full list of services synced from the Global Server (discovery)."""
    __tablename__ = "sg_service_catalog"
    id = Column(Integer, primary_key=True)
    service_id = Column(String(255), unique=True)
    gateway_code = Column(String(64))
    description = Column(String(255))
    fetched_at = Column(DateTime, default=dt.datetime.utcnow)


class MessageLog(Base):
    """Non-repudiation message log (request + response, with sig + timestamp)."""
    __tablename__ = "sg_message_log"
    id = Column(Integer, primary_key=True)
    message_id = Column(String(64))
    direction = Column(String(8))  # out | in
    consumer = Column(String(255))
    service = Column(String(255))
    request_hash = Column(String(128))
    signature = Column(Text)
    sig_verified = Column(Boolean, default=False)
    ts_serial = Column(String(64))
    ts_verified = Column(Boolean, default=False)
    response_status = Column(Integer)
    note = Column(String(512))
    created_at = Column(DateTime, default=dt.datetime.utcnow)


class AsyncMessage(Base):
    """Store-and-forward queue for asynchronous mediation (consumer side).

    The request is signed + timestamped + logged at SUBMIT time (same
    non-repudiation as the synchronous path), then delivered to the provider
    gateway by a background worker with retries; the consumer polls for the
    result (or receives it via an optional callback webhook)."""
    __tablename__ = "sg_async_message"
    id = Column(Integer, primary_key=True)
    message_id = Column(String(64), unique=True)
    direction = Column(String(8), default="out")
    consumer = Column(String(255))
    service = Column(String(255))
    body = Column(Text)                 # original request body (JSON)
    envelope = Column(Text)             # signed+timestamped envelope (JSON), ready to send
    provider_address = Column(String(255))
    callback_url = Column(String(512), nullable=True)
    status = Column(String(16), default="queued")   # queued | completed | failed
    attempts = Column(Integer, default=0)
    next_attempt = Column(DateTime)
    response = Column(Text, nullable=True)          # provider response (JSON)
    error = Column(String(512), nullable=True)
    created_at = Column(DateTime, default=dt.datetime.utcnow)
    updated_at = Column(DateTime, default=dt.datetime.utcnow, onupdate=dt.datetime.utcnow)


class GlobalConfCache(Base):
    __tablename__ = "sg_globalconf"
    id = Column(Integer, primary_key=True)
    conf_json = Column(Text)
    signature = Column(Text)
    signer_cert_pem = Column(Text)
    verified = Column(Boolean, default=False)
    fetched_at = Column(DateTime, default=dt.datetime.utcnow)
