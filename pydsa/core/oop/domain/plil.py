import math
from typing import Any
from datetime import date, datetime

from pydantic import BaseModel
from enums import PaymodeEnum



class CommonAttributes(BaseModel):
    policy_number: str
    insurer_name: str
    plan_code: str
    paymode: str
    premium_no: int
    sum_assured: float
    project_category: str
    organization_setup: str
    commencement_date: date
    total_paid: float
    next_bill_date: date
    late_fee: float = 0.0
    suspense_amount: float = 0.0
    late_fee: float = 0.0
    policy_status: str | None = None
    phone_number: str | None = None
    total_premium: float = 0.0
    total_paid_amount: float = 0.0


class Ledger(CommonAttributes):
    order_id: str
    receipt_id: str | None = None
    user_id: str | None = None
    bank_code: str | None = None
    project_code: str | None = None
    next_premium_no: int = 0
    next_total_payed_amount: float = 0.0
    next_suspense_amount: float = 0.0
    receipt_date: datetime | None = None
    count_of_installment: int = 0
    total_payable_amount: float = 0.0
    discount_amount: float = 0.0
    suspense_amount: float = 0.0
    net_received_amount: float = 0.0
    payment_status: str | None = None
    project_category: str | None = None


    def create(self) -> None:
        print("Creating Ledger Entry")

    def update(self, orderid: str, payload: dict[str, Any]) -> None:
        print(f"Updating Ledger Entry for orderid={orderid} with payload={payload}")


class Policy(CommonAttributes):
    birthday: date
    maturity_date: date
    project_code: str
    lapse_month: float = 0.0


class Insurer:
    """The class for Insurer Policy Handler. It is responsible for the all the busiess logic sanity check"""

    MINIMUM_DUE_DAYS = -90
    MAXIMUM_ADV_PAYDAYS = 20
    MINIMUM_PREMIUM_COUNT = 1
    ALLOWED_LAPSE_MONTH = 3.2

    def __init__(self, policy_obj: Policy):
        self.policy = policy_obj

    @property
    def lapsed(self) -> bool:
        return self.policy.lapse_month > self.ALLOWED_LAPSE_MONTH

    @property
    def term_in_month(self) -> int:
        match self.policy.paymode:
            case PaymodeEnum.YEARLY:
                return 12
            case PaymodeEnum.HALF_YEARLY:
                return 6
            case PaymodeEnum.QUARTERLY:
                return 3
            case _:
                return 1

    def due_count(self) -> int:
        return math.ceil(self.policy.lapse_month / self.term_in_month)

    def due_amount(self) -> float:
        current_date = datetime.today()
        next_premium_date = self.policy.next_bill_date

        diff_in_days = (next_premium_date - date(current_date.year, current_date.month, current_date.day)).days
        premium_amount = 0
        suspanse_amount = 0
        if (self.MINIMUM_DUE_DAYS <= diff_in_days <= self.MAXIMUM_ADV_PAYDAYS) or (
            self.MINIMUM_DUE_DAYS > diff_in_days and self.due_count() > 0
        ):
            premium_amount = self.policy.total_premium * max(
                self.due_count(), self.MINIMUM_PREMIUM_COUNT
            )
            suspanse_amount = self.policy.suspense_amount or 0
        return (premium_amount + self.policy.late_fee) - suspanse_amount

    def ledger(self, order_id: str) -> Ledger:
        return Ledger(
            **self.policy.model_dump(), order_id=order_id
        )