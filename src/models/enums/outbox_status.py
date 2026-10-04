import enum


class OutboxStatus(enum.StrEnum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    PROCESSING = "processing"
