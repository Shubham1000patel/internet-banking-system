from database import create_connection

from repositories.account_repository import AccountRepository
from repositories.bill_payment_repository import BillPaymentRepository
from repositories.transaction_repository import TransactionRepository
from exceptions import (
    BankingError,
    InvalidAmountError,
    InactiveAccountError,
    InsufficientBalanceError
)


class BillPaymentService:

    def __init__(self):
        self.account_repository = AccountRepository()
        self.bill_payment_repository = BillPaymentRepository()

    def pay_bill(
        self,
        customer_id,
        account_number,
        bill_type,
        bill_number,
        provider_name,
        amount
    ):
        connection = create_connection()

        try:
            # 1. Find account
            account = (
                self.account_repository
                .get_account_by_number(account_number)
            )

            if account is None:
                raise BankingError(
                    "Account not found."
                )

            # 2. Ownership check
            if account[2] != customer_id:
                raise BankingError(
                    "You are not authorized to use this account."
                )

            # 3. Account status
            if account[5] != "ACTIVE":
                raise InactiveAccountError(
                    "Account is not active."
                )

            # 4. Validate bill type
            allowed_bill_types = [
                "ELECTRICITY",
                "MOBILE",
                "INTERNET",
                "WATER",
                "CREDIT_CARD"
            ]

            bill_type = bill_type.upper()

            if bill_type not in allowed_bill_types:
                raise BankingError(
                    "Invalid bill type."
                )

            # 5. Validate bill number
            if not bill_number.strip():
                raise BankingError(
                    "Bill number is required."
                )

            # 6. Validate provider
            if not provider_name.strip():
                raise BankingError(
                    "Provider name is required."
                )

            # 7. Validate amount
            if amount <= 0:
                raise InvalidAmountError(
                    "Bill amount must be greater than zero."
                )

            # 8. Check balance
            if amount > account[4]:
                raise InsufficientBalanceError(
                    "Insufficient balance."
                )

            # 9. Calculate new balance
            new_balance = account[4] - amount

            # 10. Update account balance
            self.account_repository.update_balance(
                account_number,
                new_balance,
                connection
            )

            # 11. Create transaction
            transaction_repository = (
                TransactionRepository()
            )

            transaction_id = (
                transaction_repository
                .create_transaction_with_connection(
                    from_account=account_number,
                    to_account=None,
                    transaction_type="BILL_PAYMENT",
                    amount=amount,
                    status="SUCCESS",
                    description=f"{bill_type} Bill Payment",
                    connection=connection
                )
            )

            # 12. Create bill payment record
            bill_payment_id = (
    self.bill_payment_repository
    .create_bill_payment_with_connection(
        customer_id=customer_id,
        account_number=account_number,
        bill_type=bill_type,
        bill_number=bill_number,
        provider_name=provider_name,
        amount=amount,
        status="SUCCESS",
        transaction_id=transaction_id,
        connection=connection
    )
)

            # 13. Commit everything
            connection.commit()

            return {
                "message": "Bill payment successful.",
                "bill_payment_id": bill_payment_id,
                "transaction_id": transaction_id,
                "account_number": account_number,
                "bill_type": bill_type,
                "bill_number": bill_number,
                "amount": amount,
                "status": "SUCCESS",
                "balance": new_balance
            }

        except Exception:
            connection.rollback()
            raise

        finally:
            connection.close()

    def get_customer_bill_payments(
        self,
        customer_id
    ):
        bill_payments = (
            self.bill_payment_repository
            .get_bill_payments_by_customer(customer_id)
        )

        return [
            {
                "bill_payment_id": bill[0],
                "customer_id": bill[1],
                "account_number": bill[2],
                "bill_type": bill[3],
                "bill_number": bill[4],
                "provider_name": bill[5],
                "amount": bill[6],
                "status": bill[7],
                "transaction_id": bill[8],
                "payment_date": bill[9]
            }
            for bill in bill_payments
        ]

    def get_bill_payment(
        self,
        customer_id,
        bill_payment_id
    ):
        bill = (
            self.bill_payment_repository
            .get_bill_payment_by_id(bill_payment_id)
        )

        if bill is None:
            raise BankingError(
                "Bill payment not found."
            )

        # Ownership check
        if bill[1] != customer_id:
            raise BankingError(
                "You are not authorized to access this bill payment."
            )

        return {
            "bill_payment_id": bill[0],
            "customer_id": bill[1],
            "account_number": bill[2],
            "bill_type": bill[3],
            "bill_number": bill[4],
            "provider_name": bill[5],
            "amount": bill[6],
            "status": bill[7],
            "transaction_id": bill[8],
            "payment_date": bill[9]
        }