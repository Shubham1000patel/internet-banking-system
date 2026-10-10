from repositories.admin_repository import AdminRepository
from repositories.customer_repository import CustomerRepository
from repositories.account_repository import AccountRepository
from repositories.transaction_repository import TransactionRepository

from exceptions import BankingError
from security import (
    verify_password,
    create_admin_access_token
)


class AdminService:

    def __init__(self):

        self.admin_repository = AdminRepository()
        self.customer_repository = CustomerRepository()
        self.account_repository = AccountRepository()
        self.transaction_repository = TransactionRepository()

    def login(self, email, password):

        admin = self.admin_repository.get_admin_by_email(email)

        if admin is None:
            raise BankingError("Incorrect admin credentials.")

        if admin[5] != "ACTIVE":
            raise BankingError("Admin account is not active.")

        if not verify_password(password, admin[3]):
            raise BankingError("Incorrect admin credentials.")

        access_token = create_admin_access_token(
            admin_id=admin[0],
            email=admin[2],
            role=admin[4]
        )

        return {
            "admin_id": admin[0],
            "name": admin[1],
            "email": admin[2],
            "role": admin[4],
            "access_token": access_token,
            "token_type": "bearer",
            "message": "Admin login successful."
        }

    def get_dashboard_summary(self):

        total_customers = (
            self.customer_repository.count_customers()
        )

        total_accounts = (
            self.account_repository.count_accounts()
        )

        transaction_summary = (
            self.transaction_repository
            .get_transaction_summary()
        )

        return {
            "total_customers": total_customers,
            "total_accounts": total_accounts,
            "total_transactions": transaction_summary[0],
            "total_transaction_amount": transaction_summary[1],
            "successful_transactions": transaction_summary[2] or 0,
            "failed_transactions": transaction_summary[3] or 0
        }


    def get_financial_summary(self):

        results = (
            self.transaction_repository
            .get_financial_summary()
        )

        report = []

        for row in results:

            report.append({
                "transaction_type": row[0],
                "transaction_count": row[1],
                "total_amount": row[2]
            })

        return report