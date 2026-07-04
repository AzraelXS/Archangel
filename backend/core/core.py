import logging
import time

from core.es_client import get_es_client

logging.basicConfig(level=logging.INFO, format="%(asctime)s core %(levelname)s %(message)s")
log = logging.getLogger("core")


def wait_for_es():
    es = get_es_client()
    while True:
        try:
            if es.ping():
                log.info("connected to elasticsearch")
                return es
        except Exception as exc:
            log.warning("waiting for elasticsearch: %s", exc)
        time.sleep(3)


def main():
    wait_for_es()
    log.info("archangel core online")
    while True:
        time.sleep(60)


if __name__ == "__main__":
    main()
