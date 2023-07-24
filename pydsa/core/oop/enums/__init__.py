from enum import Enum

class PaymodeEnum(str, Enum):
    YEARLY = "1"
    HALF_YEARLY = "6"
    QUARTERLY = "3"
    MONTHLY = "5"
