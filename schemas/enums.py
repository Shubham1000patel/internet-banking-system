from enum import Enum


class AccountType(str, Enum):
    SAVINGS = "SAVINGS"
    CURRENT = "CURRENT"


class AccountStatus(str, Enum):
    ACTIVE = "ACTIVE"
    BLOCKED = "BLOCKED"


class TransactionType(str, Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAW = "WITHDRAW"
    TRANSFER = "TRANSFER"
    BILL_PAYMENT = "BILL_PAYMENT"


class TransactionStatus(str, Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class BillType(str, Enum):
    ELECTRICITY = "ELECTRICITY"
    MOBILE = "MOBILE"
    INTERNET = "INTERNET"
    WATER = "WATER"
    CREDIT_CARD = "CREDIT_CARD"