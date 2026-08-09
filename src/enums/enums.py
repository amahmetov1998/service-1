import enum


class UserStatus(enum.StrEnum):
    ACTIVE = "active"
    BLOCKED = "blocked"
    DELETED = "deleted"


class PhoneSyncStatus(enum.StrEnum):
    PENDING = "pending"
    DONE = "done"


class PhoneType(enum.StrEnum):
    MOBILE = "mobile"
    HOME = "home"
    WORK = "work"


class OperatorType(enum.StrEnum):
    MTS = "mts"
    MEGAFON = "megafon"
    BEELINE = "beeline"


class RegionType(enum.StrEnum):
    MOSCOW_CITY = "moscow_city"
    SAINT_PETERSBURG = "saint_petersburg"
    MOSCOW_OBLAST = "moscow_oblast"
    KRASNODAR_KRAI = "krasnodar_krai"
    REPUBLIC_OF_TATARSTAN = "republic_of_tatarstan"
    OTHER = "other"
