from fastapi import FastAPI ,Header,HTTPException
from datetime import datetime
import secrets
import string
from fastapi import Depends
from fastapi import Query
from fastapi.middleware.cors import CORSMiddleware
from dependencies import get_current_customer
from schemas.customer_schema import (
    CustomerRegisterRequest,
    CustomerRegisterResponse
)
from schemas.admin_schema import (
    AdminLoginRequest,
    AdminLoginResponse,
    AdminCustomerResponse,
    CustomerStatusUpdateRequest,
    CustomerStatusUpdateResponse,
    AccountStatusUpdateRequest,
    AccountStatusUpdateResponse,
    AdminDashboardResponse,
    FinancialSummaryResponse
)
from exception_handlers import register_exception_handlers
from services.admin_service import AdminService
from admin_dependencies import get_current_admin


from schemas.auth_schema import (
    LoginRequest,
    LoginResponse
)
from schemas.account_schema import (
    AccountCreateRequest,
    AccountResponse,
    AccountBalanceResponse,
    DepositRequest,
    DepositResponse,
    WithdrawResponse,
    TransferRequest,
    TransferResponse,
    TransactionResponse,
    BeneficiaryCreateRequest,
    BeneficiaryResponse,
    BeneficiaryUpdateRequest,
    BillPaymentRequest,
    BillPaymentResponse,
    BillPaymentHistoryResponse


)
from services.beneficiary_service import BeneficiaryService
from services.bill_payment_service import BillPaymentService
from services.customer_service import CustomerService
from services.authentication_service import AuthenticationService
from schemas.profile_schema import CustomerProfileResponse,ChangePasswordRequest,UpdateProfileRequest
from schemas.account_schema import AccountResponse
from services.account_service import AccountService

from schemas.account_schema import (
    AccountResponse,
    AccountBalanceResponse
)

app = FastAPI(
    title="Internet Banking System",
    description="Educational Internet Banking Backend",
    version="1.0.0"
)
register_exception_handlers(app)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
customer_service = CustomerService()
authentication_service = AuthenticationService()
account_service = AccountService()
beneficiary_service = BeneficiaryService()
bill_payment_service = BillPaymentService()
admin_service = AdminService()

@app.get("/")
def home():
    return {
        "message": "Internet Banking API is running."
    }


@app.get("/health")
def health_check():
    return {
        "status": "UP"
    }

@app.post("/admin/login", response_model=AdminLoginResponse)
def admin_login(request: AdminLoginRequest):

    result = admin_service.login(
        email=request.email,
        password=request.password
    )

    return result    

@app.get(
    "/admin/customers",
    response_model=list[AdminCustomerResponse]
)
def get_all_customers(
    current_admin: dict = Depends(get_current_admin)
):

    return customer_service.get_all_customers()

@app.get(
    "/admin/accounts",
    response_model=list[AccountResponse]
)
def get_all_accounts(
    current_admin: dict = Depends(get_current_admin)
):

    return account_service.get_all_accounts()


@app.get(
    "/admin/transactions",
    response_model=list[TransactionResponse]
)
def get_all_transactions(
    current_admin: dict = Depends(get_current_admin)
):

    return account_service.get_all_transactions()

@app.put(
    "/admin/customers/{customer_id}/status",
    response_model=CustomerStatusUpdateResponse
)
def update_customer_status(
    customer_id: int,
    request: CustomerStatusUpdateRequest,
    current_admin: dict = Depends(get_current_admin)
):

    return customer_service.update_customer_status(
        customer_id=customer_id,
        status=request.status
    ) 

@app.put(
    "/admin/accounts/{account_number}/status",
    response_model=AccountStatusUpdateResponse
)
def update_account_status(
    account_number: str,
    request: AccountStatusUpdateRequest,
    current_admin: dict = Depends(get_current_admin)
):

    return account_service.update_account_status(
        account_number=account_number,
        status=request.status
    ) 

@app.get(
    "/admin/transactions/search",
    response_model=list[TransactionResponse]
)
def search_transactions(
    account_number: str | None = Query(default=None),
    transaction_type: str | None = Query(default=None),
    status: str | None = Query(default=None),
    current_admin: dict = Depends(get_current_admin)
):

    return account_service.search_transactions(
        account_number=account_number,
        transaction_type=transaction_type,
        status=status
    )

@app.get(
    "/admin/dashboard",
    response_model=AdminDashboardResponse
)
def get_admin_dashboard(
    current_admin: dict = Depends(get_current_admin)
):

    return admin_service.get_dashboard_summary() 

@app.get(
    "/admin/reports/financial",
    response_model=list[FinancialSummaryResponse]
)
def get_financial_summary(
    current_admin: dict = Depends(get_current_admin)
):

    return admin_service.get_financial_summary()


@app.post(
    "/auth/register",
    
    response_model=CustomerRegisterResponse
)
def register_customer(request: CustomerRegisterRequest):

    customer_id = customer_service.register_customer(
        name=request.name,
        email=request.email,
        phone=request.phone,
        address=request.address,
        date_of_birth=request.date_of_birth,
        password=request.password
    )

    return {
        "message": "Customer registered successfully.",
        "customer_id": customer_id
    }


@app.post(
    "/auth/login",
    response_model=LoginResponse
)
def login_customer(request: LoginRequest):

    result = authentication_service.login(
        login_id=request.login_id,
        password=request.password
    )

    return result

@app.post("/accounts", response_model=AccountResponse, status_code=201)
def create_my_account(
    request: AccountCreateRequest,
    current_customer: dict = Depends(get_current_customer)
):
    # Generate an account number on the backend.
    account_number = "".join(
        secrets.choice(string.digits) for _ in range(12)
    )
    try:
        result = account_service.create_account(
            customer_id=current_customer["customer_id"],
            account_number=account_number,
            account_type=request.account_type,
            initial_balance=request.initial_balance
        )
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )    

    return account_service.get_account_balance(
        customer_id=current_customer["customer_id"],
        account_number=account_number
    ) | {
        "account_id": result,
        "customer_id": current_customer["customer_id"],
        "account_type": request.account_type,
        "status": "ACTIVE",
        "created_at": datetime.now(),
    }

@app.get("/customers/me")
def get_my_profile(
    current_customer: dict = Depends(get_current_customer)
):
    return {
        "message": "Authenticated customer.",
        "customer": current_customer
    }


@app.get(
    "/customers/me",
    response_model=CustomerProfileResponse
)
def get_my_profile(
    current_customer: dict = Depends(get_current_customer)
):

    customer = customer_service.get_customer_profile(
        current_customer["customer_id"]
    )

    return customer

account_service = AccountService()

@app.post("/customers/me/change-password")
def change_customer_password(
    request: ChangePasswordRequest,
    current_customer: dict = Depends(get_current_customer)
):
    return customer_service.change_password(
        customer_id=current_customer["customer_id"],
        current_password=request.current_password,
        new_password=request.new_password,
        confirm_password=request.confirm_password
    )

@app.put("/customers/me/profile")
def update_customer_profile(
    request: UpdateProfileRequest,
    current_customer: dict = Depends(get_current_customer)
):
    return customer_service.update_profile(
        customer_id=current_customer["customer_id"],
        phone=request.phone,
        address=request.address
    )

@app.get(
    "/accounts",
    response_model=list[AccountResponse]
)
def get_my_accounts(
    current_customer: dict = Depends(get_current_customer)
):

    accounts = account_service.get_customer_accounts(
        current_customer["customer_id"]
    )

    return accounts


@app.get(
    "/accounts/{account_number}/balance",
    response_model=AccountBalanceResponse
)
def get_account_balance(
    account_number: str,
    current_customer: dict = Depends(get_current_customer)
):

    balance = account_service.get_account_balance(
        customer_id=current_customer["customer_id"],
        account_number=account_number
    )

    return balance


@app.post(
    "/accounts/{account_number}/deposit",
    response_model=DepositResponse
)
def deposit_money(
    account_number: str,
    request: DepositRequest,
    current_customer: dict = Depends(get_current_customer)
):

    result = account_service.deposit_money(
        customer_id=current_customer["customer_id"],
        account_number=account_number,
        amount=request.amount
    )

    return result


@app.post(
    "/accounts/{account_number}/withdraw",
    response_model=WithdrawResponse
)
def withdraw_money(
    account_number: str,
    request: DepositRequest,
    current_customer: dict = Depends(get_current_customer)
):

    result = account_service.withdraw_money(
        customer_id=current_customer["customer_id"],
        account_number=account_number,
        amount=request.amount
    )

    return result

@app.post("/transfers", response_model=TransferResponse)
def transfer_money(
    request: TransferRequest,
    idempotency_key: str = Header(
        alias="Idempotency-Key",
        min_length=1,
        max_length=100
    ),
    current_customer: dict = Depends(get_current_customer)
):
    return account_service.transfer_money(
        customer_id=current_customer["customer_id"],
        from_account_number=request.from_account,
        to_account_number=request.to_account,
        amount=request.amount,
        idempotency_key=idempotency_key
    )


@app.get(
    "/accounts/{account_number}/transactions",
    response_model=list[TransactionResponse]
)
def get_account_transactions(
    account_number: str,
    current_customer: dict = Depends(get_current_customer)
):

    transactions = account_service.get_account_transactions(
        customer_id=current_customer["customer_id"],
        account_number=account_number
    )

    return transactions


@app.post("/beneficiaries")
def add_beneficiary(
    request: BeneficiaryCreateRequest,
    current_customer: dict = Depends(get_current_customer)
):

    result = beneficiary_service.add_beneficiary(
        customer_id=current_customer["customer_id"],
        name=request.name,
        account_number=request.account_number,
        bank_name=request.bank_name
    )

    return result


@app.get(
    "/beneficiaries",
    response_model=list[BeneficiaryResponse]
)
def get_my_beneficiaries(
    current_customer: dict = Depends(get_current_customer)
):
    return beneficiary_service.get_customer_beneficiaries(
        current_customer["customer_id"]
    )

@app.get(
    "/beneficiaries/{beneficiary_id}",
    response_model=BeneficiaryResponse
)
def get_beneficiary(
    beneficiary_id: int,
    current_customer: dict = Depends(get_current_customer)
):
    return beneficiary_service.get_beneficiary(
        customer_id=current_customer["customer_id"],
        beneficiary_id=beneficiary_id
    )

@app.put("/beneficiaries/{beneficiary_id}")
def update_beneficiary(
    beneficiary_id: int,
    request: BeneficiaryUpdateRequest,
    current_customer: dict = Depends(get_current_customer)
):
    return beneficiary_service.update_beneficiary(
        customer_id=current_customer["customer_id"],
        beneficiary_id=beneficiary_id,
        name=request.name,
        account_number=request.account_number,
        bank_name=request.bank_name
    )


@app.delete("/beneficiaries/{beneficiary_id}")
def delete_beneficiary(
    beneficiary_id: int,
    current_customer: dict = Depends(get_current_customer)
):
    return beneficiary_service.delete_beneficiary(
        customer_id=current_customer["customer_id"],
        beneficiary_id=beneficiary_id
    )


@app.post(
    "/bill-payments",
    response_model=BillPaymentResponse
)
def pay_bill(
    request: BillPaymentRequest,
    current_customer: dict = Depends(get_current_customer)
):

    return bill_payment_service.pay_bill(
        customer_id=current_customer["customer_id"],
        account_number=request.account_number,
        bill_type=request.bill_type,
        bill_number=request.bill_number,
        provider_name=request.provider_name,
        amount=request.amount
    )


@app.get(
    "/bill-payments/{bill_payment_id}",
    response_model=BillPaymentHistoryResponse
)
def get_bill_payment(
    bill_payment_id: int,
    current_customer: dict = Depends(get_current_customer)
):

    return bill_payment_service.get_bill_payment(
        customer_id=current_customer["customer_id"],
        bill_payment_id=bill_payment_id
    )




@app.get(
    "/bill-payments",
    response_model=list[BillPaymentHistoryResponse]
)
def get_my_bill_payments(
    current_customer: dict = Depends(get_current_customer)
):
    return bill_payment_service.get_customer_bill_payments(
        customer_id=current_customer["customer_id"]
    )    

