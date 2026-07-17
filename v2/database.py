import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import declarative_base
from common.dbutil import init_db, make_session_factory, SessionProxy
from security_gateway import config

Base = declarative_base()
engine = None
SessionLocal = SessionProxy()


def init():
    global engine
    import security_gateway.models  # noqa: F401
    engine = init_db(config.DB_NAME, Base)
    SessionLocal.configure(make_session_factory(engine))
