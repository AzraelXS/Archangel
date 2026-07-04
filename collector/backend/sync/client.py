import logging
import os
import time
from pathlib import Path

import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s sync-agent %(levelname)s %(message)s")
log = logging.getLogger("sync-agent")

STATE_DIR = Path("/app/state")
COLLECTOR_ID_FILE = STATE_DIR / "collector_id"


def get_cached_collector_id() -> str | None:
    """Non-blocking read of the collector_id sync-agent already established.
    Callers (e.g. the shipper) should use this instead of register() so
    that only one process ever performs the registration HTTP round trip."""
    if COLLECTOR_ID_FILE.exists():
        return COLLECTOR_ID_FILE.read_text().strip()
    return None


def register() -> str:
    """Registers this collector with the cloud tenant, or reuses a saved collector_id."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    if COLLECTOR_ID_FILE.exists():
        collector_id = COLLECTOR_ID_FILE.read_text().strip()
        log.info("reusing saved collector_id %s", collector_id)
        return collector_id

    cloud_api_url = os.environ["CLOUD_API_URL"].rstrip("/")
    api_key = os.environ["TENANT_API_KEY"]
    name = os.environ.get("COLLECTOR_NAME", "collector-01")

    while True:
        try:
            resp = requests.post(
                f"{cloud_api_url}/collectors/register",
                json={"api_key": api_key, "name": name},
                timeout=10,
            )
            resp.raise_for_status()
            collector_id = resp.json()["collector_id"]
            COLLECTOR_ID_FILE.write_text(collector_id)
            log.info("registered with cloud, collector_id=%s", collector_id)
            return collector_id
        except requests.RequestException as exc:
            log.warning("registration failed, retrying in 10s: %s", exc)
            time.sleep(10)


def main():
    collector_id = register()
    log.info("sync agent online, collector_id=%s", collector_id)
    # The periodic shipper task (sync.shipper.ship_backlog) does the actual
    # data push and runs on the celery-beat schedule; this process just
    # owns registration/identity for now.
    while True:
        time.sleep(60)


if __name__ == "__main__":
    main()
