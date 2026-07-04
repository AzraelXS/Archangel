"""
Shared wire format for records shipped from a collector to the cloud
ingest API. Both the collector's local writers (listeners, core) and the
cloud ingest endpoint's validation are expected to agree on this shape.
"""
from dataclasses import asdict, dataclass, field
from typing import Any, Literal

EventKind = Literal["event", "metric"]


@dataclass
class NormalizedRecord:
    kind: EventKind
    source: str          # e.g. "syslog", "snmp-trap", "smtp", "polling-engine"
    timestamp: str       # ISO-8601 UTC
    message: str
    fields: dict[str, Any] = field(default_factory=dict)
    shipped: bool = False

    def to_dict(self) -> dict:
        return asdict(self)
