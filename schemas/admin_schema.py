from pydantic import BaseModel
from datetime import datetime ,date
from decimal import Decimal
from schemas.enums import AccountStatus

class AdminLoginRequest(BaseModel):
    email: str
    password: str


class AdminLoginResponse(BaseModel):
    admin_id: int
    name: str
    email: str
    role: str
    access_token: str
    token_type: str
    message: str


class AdminCustomerResponse(BaseModel):
    customer_id: int
    name: str
    email: str
    phone: str
    address: str | None
    date_of_birth: date | None
    status: str
    created_at: datetime    



class CustomerStatusUpdateRequest(BaseModel):
    status: AccountStatus


class CustomerStatusUpdateResponse(BaseModel):
    message: str
    customer_id: int
    status: str    


class AccountStatusUpdateRequest(BaseModel):
    status: AccountStatus


class AccountStatusUpdateResponse(BaseModel):
    message: str
    account_number: str
    status: str     

class AdminDashboardResponse(BaseModel):

    total_customers: int
    total_accounts: int
    total_transactions: int
    total_transaction_amount: Decimal
    successful_transactions: int
    failed_transactions: int    

class FinancialSummaryResponse(BaseModel):

    transaction_type: str
    transaction_count: int
    total_amount: Decimal    