from enum import StrEnum


class NotificationType(StrEnum):
    WELCOME = "Welcome"
    EMAIL_VERIFIED = "Email Verified"
    PASSWORD_CHANGED = "Password Changed"
