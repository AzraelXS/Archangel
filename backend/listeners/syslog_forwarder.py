import os
import socket


def forward_syslog(message: str):
    """Send a syslog-formatted message to the core's syslog ingest port."""
    host = os.environ.get("SYSLOG_FORWARD_HOST", "core")
    port = int(os.environ.get("SYSLOG_FORWARD_PORT", "5514"))
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.sendto(message.encode("utf-8"), (host, port))
    finally:
        sock.close()
