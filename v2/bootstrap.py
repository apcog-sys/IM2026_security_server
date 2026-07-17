"""Materialize a gateway's TLS material to disk BEFORE uvicorn starts.

uvicorn loads its SSL context at process start (before the app runs), so the
mutual-TLS message port needs the gateway's auth cert/key and the CA cert as
files up front. This script:
  1. ensures the gateway has an authentication identity (key + CA-issued auth
     cert) in its database (requesting one from the CA if needed),
  2. writes  certs/<GATEWAY_CODE>/auth.crt , auth.key  and  certs/ca.crt .

Run once per gateway (with that gateway's env) before launching uvicorn.
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import httpx

from common.topology import CA_URL
from security_gateway import config, database, sg_core


def _write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def _wait_for_ca():
    for _ in range(40):
        try:
            if httpx.get(f"{CA_URL}/api/ca-cert", timeout=3).status_code == 200:
                return True
        except Exception:
            pass
        time.sleep(1)
    return False


def main():
    database.init()
    if not _wait_for_ca():
        raise SystemExit(f"[{config.GATEWAY_CODE}] CA not reachable at {CA_URL}")
    last = None
    for attempt in range(5):
        try:
            ident = sg_core.provision_identity()   # creates identity via CA if missing
            _write(config.AUTH_CRT, ident.auth_cert_pem)
            _write(config.AUTH_KEY, ident.auth_key_pem)
            _write(config.CA_CRT, httpx.get(f"{CA_URL}/api/ca-cert", timeout=15).text)
            print(f"[{config.GATEWAY_CODE}] TLS material written to {config.CERT_DIR}")
            return
        except Exception as e:
            last = e
            print(f"[{config.GATEWAY_CODE}] bootstrap attempt {attempt+1} failed: {e}")
            time.sleep(2)
    raise SystemExit(f"[{config.GATEWAY_CODE}] bootstrap failed: {last}")


if __name__ == "__main__":
    main()
