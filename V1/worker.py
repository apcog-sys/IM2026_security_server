"""Background delivery worker for asynchronous messages.

Runs as an asyncio task inside the gateway process. It polls the async
queue and delivers due messages to the provider gateway. Delivery itself
uses blocking I/O (mutual-TLS httpx), so it is run in a thread to avoid
blocking the event loop.
"""
import asyncio

from security_gateway import asyncq, config, proxy

POLL_INTERVAL = 1.0   # seconds


async def worker_loop():
    while True:
        try:
            for message_id in asyncq.due_batch():
                await asyncio.to_thread(proxy.deliver_one, message_id)
        except Exception as e:                       # never let the loop die
            print(f"[async-worker] error: {e}")
        await asyncio.sleep(POLL_INTERVAL)


def start(app):
    # A gateway runs two processes (admin + mTLS message) sharing one DB. Only
    # ONE should run the delivery worker, to avoid double-sending. Gated by
    # config.RUN_WORKER (SG_RUN_WORKER); start_all sets it false for the mTLS process.
    if not config.RUN_WORKER:
        return

    @app.on_event("startup")
    async def _start_worker():
        asyncio.create_task(worker_loop())
        print("[async-worker] started")
