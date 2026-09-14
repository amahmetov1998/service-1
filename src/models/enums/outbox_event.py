import enum


class TaskStatus(enum.StrEnum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    PROCESSING = "processing"


class EventType(enum.StrEnum):
    NOTIFICATION_CREATE = "notification_create"
