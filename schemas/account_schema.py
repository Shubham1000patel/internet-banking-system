from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal
from schemas.enums import BillType,AccountType,AccountStatus,TransactionType,TransactionStatus



from typing import Literal


class AccountCreateRequest(BaseModel):
    account_type: Literal["SAVINGS", "CURRENT"]
    initial_balance: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
        max_digits=12,
        decimal_places=2
    )

class AccountResponse(BaseModel):
    account_id: int
    account_number: str
    customer_id: int
    account_type: AccountType
    balance: Decimal
    status: AccountStatus
    created_at: datetime


class AccountBalanceResponse(BaseModel):
    account_number: str
    balance: Decimal


class DepositRequest(BaseModel):
    amount: Decimal = Field(gt=0, max_digits=15, decimal_places=2)


class DepositResponse(BaseModel):
    message: str
    transaction_id: int
    account_number: str
    amount: Decimal
    balance: Decimal



class WithdrawResponse(BaseModel):
    message: str
    transaction_id: int
    account_number: str
    amount: Decimal
    balance: Decimal

class TransferRequest(BaseModel):
    from_account: str
    to_account: str
    amount: Decimal = Field(gt=0, max_digits=15, decimal_places=2)

class TransferResponse(BaseModel):
    message: str
    transaction_id: int
    from_account: str   
    to_account: str
    amount: Decimal
    balance: Decimal


class TransactionResponse(BaseModel):
    transaction_id: int
    from_account: str | None
    to_account: str | None
    transaction_type: TransactionType
    amount: Decimal
    status: TransactionStatus
    description: str | None
    transaction_date: datetime    

class BeneficiaryCreateRequest(BaseModel):
    name: str
    account_number: str
    bank_name: str

class BeneficiaryUpdateRequest(BaseModel):
    name: str
    account_number: str
    bank_name: str


class BeneficiaryResponse(BaseModel):
    beneficiary_id: int
    customer_id: int
    name: str
    account_number: str
    bank_name: str
    status: str
    created_at: datetime


class BillPaymentRequest(BaseModel):
    account_number: str
    bill_type: BillType
    bill_number: str = Field(min_length=1, max_length=50)
    provider_name: str = Field(min_length=1, max_length=100)
    amount: Decimal = Field(
        gt=0,
        max_digits=15,
        decimal_places=2
    )

class BillPaymentResponse(BaseModel):
    message: str
    bill_payment_id: int
    transaction_id: int
    account_number: str
    bill_type: str
    bill_number: str
    amount: Decimal
    status: str
    balance: Decimal


class BillPaymentHistoryResponse(BaseModel):
    bill_payment_id: int
    customer_id: int
    account_number: str
    bill_type: str
    bill_number: str
    provider_name: str | None
    amount: Decimal
    status: str
    transaction_id: int | None
    payment_date: datetime    


class WithdrawRequest(BaseModel):
    amount: Decimal = Field(
        gt=0,
        max_digits=15,
        decimal_places=2
    )    