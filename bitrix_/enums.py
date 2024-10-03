from enum import IntEnum, StrEnum


class DealCategory(IntEnum):
    OVK = 16  # (Вводные 2.0) = ОВК
    OK = 17  # (Консультация 2.0) = ОК
    CHE = 14  # Чек-ап ТУР


class Hopper(StrEnum):
    OVK = "ОВК"
    OK = "ОК"