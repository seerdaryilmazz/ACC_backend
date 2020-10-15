from enum import IntEnum


class EmailTypes(IntEnum):
    ResetPassword = 0


class TrendReportsType(IntEnum):
    QUARTER = 0
    MONTH = 1
    WEEK = 2


class HubType(IntEnum):
    ALL = 0
    ANATOLIAN_SIDE = 4
    EUROPEAN_SIDE = 5
