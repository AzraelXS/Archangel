"""
SNMP trap listener: receives SNMP traps and re-emits them as syslog messages
so they can flow through the same workflow-automation pipeline as syslog.
Placeholder using pysnmp's asyncio trap receiver.
"""
import logging
import time

logging.basicConfig(level=logging.INFO, format="%(asctime)s snmp-trap %(levelname)s %(message)s")
log = logging.getLogger("snmp-trap-listener")


def main():
    log.info("snmp trap listener online (stub)")
    while True:
        time.sleep(60)


if __name__ == "__main__":
    main()
