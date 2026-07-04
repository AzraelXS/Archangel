"""
SMTP listener: accepts raw SMTP messages and re-emits them as syslog messages
to feed the same workflow-automation pipeline. Placeholder using aiosmtpd.
"""
import asyncio
import logging

from aiosmtpd.controller import Controller

from listeners.syslog_forwarder import forward_syslog

logging.basicConfig(level=logging.INFO, format="%(asctime)s smtp-listener %(levelname)s %(message)s")
log = logging.getLogger("smtp-listener")


class SyslogBridgeHandler:
    async def handle_DATA(self, server, session, envelope):
        forward_syslog(envelope.content.decode("utf-8", errors="replace"))
        return "250 Message accepted for delivery"


def main():
    controller = Controller(SyslogBridgeHandler(), hostname="0.0.0.0", port=1025)
    controller.start()
    log.info("smtp listener online on :1025")
    try:
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        controller.stop()


if __name__ == "__main__":
    main()
