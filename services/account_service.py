from repositories.account_repository import AccountRepository
import hashlib
import json

from repositories.idempotency_repository import IdempotencyRepository
from repositories.customer_repository import CustomerRepository
from exceptions import (
    BankingError,
    InvalidAmountError,
    InactiveAccountError,
    InsufficientBalanceError
)
from repositories.transaction_repository import TransactionRepository
from database import create_connection


class AccountService:

    def __init__(self):
        self.account_repository = AccountRepository()
        self.customer_repository = CustomerRepository()
        self.idempotency_repository = IdempotencyRepository()

    def create_account(self,customer_id,account_number,account_type,initial_balance=0.00):

        # Get all accounts belonging to this customer
        existing_accounts = self.get_customer_accounts(customer_id)

        # Prevent duplicate account types
        for account in existing_accounts:
            if account["account_type"] == account_type:
                raise ValueError(
                    f"You already have a {account_type.lower()} account."
                )

        # 1. Check customer exists
        customer = self.customer_repository.get_customer_by_id(
            customer_id
        )

        if customer is None:
            raise BankingError("Customer not found.")

        # 2. Check customer status
        # customers table:
        # customer_id, name, email, phone, address,
        # date_of_birth, password_hash, status, created_at

        if customer[7] != "ACTIVE":
            raise BankingError("Customer is not active.")

        # 3. Validate account type
        allowed_account_types = ["SAVINGS", "CURRENT"]

        if account_type not in allowed_account_types:
            raise BankingError(
                "Invalid account type. Use SAVINGS or CURRENT."
            )

        # 4. Validate initial balance
        if initial_balance < 0:
            raise BankingError(
                "Initial balance cannot be negative."
            )

        # 5. Check account number already exists
        existing_account = self.account_repository.get_account_by_number(
            account_number
        )

        if existing_account is not None:
            raise BankingError(
                "Account number already exists."
            )

        # 6. Create account
        account_id = self.account_repository.create_account(
            account_number=account_number,
            customer_id=customer_id,
            account_type=account_type,
            balance=initial_balance
        )

        return account_id
    

    def get_customer_accounts(self, customer_id):

        customer = self.customer_repository.get_customer_by_id(
            customer_id
        )

        if customer is None:
            raise BankingError("Customer not found.")

        if customer[7] != "ACTIVE":
            raise BankingError("Customer is not active.")

        accounts = self.account_repository.get_accounts_by_customer(
            customer_id
        )

        return [
            {
                "account_id": account[0],
                "account_number": account[1],
                "customer_id": account[2],
                "account_type": account[3],
                "balance": account[4],
                "status": account[5],
                "created_at": account[6]
            }
            for account in accounts
        ]


    def get_account_balance(
    self,
    customer_id,
    account_number
):

        account = self.account_repository.get_account_by_number(
            account_number
        )

        if account is None:
            raise BankingError("Account not found.")

        if account[2] != customer_id:
            raise BankingError(
                "You are not authorized to access this account."
            )

        if account[5] != "ACTIVE":
            raise BankingError(
                "Account is not active."
            )

        return {
            "account_number": account[1],
            "balance": account[4]
        }


    def deposit_money(self, customer_id, account_number, amount):
        if amount <= 0:
            raise InvalidAmountError(
                "Deposit amount must be greater than zero."
            )

        connection = create_connection()

        try:
            connection.start_transaction()

            account = self.account_repository.get_account_by_number_for_update(
                account_number, connection
            )

            if account is None:
                raise BankingError("Account not found.")

            if account[2] != customer_id:
                raise BankingError(
                    "You are not authorized to access this account."
                )

            if account[5] != "ACTIVE":
                raise InactiveAccountError("Account is not active.")

            new_balance = account[4] + amount

            self.account_repository.update_balance(
                account_number, new_balance, connection
            )

            transaction_repository = TransactionRepository()

            transaction_id = transaction_repository.create_transaction_with_connection(
                from_account=None,
                to_account=account_number,
                transaction_type="DEPOSIT",
                amount=amount,
                status="SUCCESS",
                description="Cash Deposit",
                connection=connection
            )

            connection.commit()

            return {
                "message": "Money deposited successfully.",
                "transaction_id": transaction_id,
                "account_number": account_number,
                "amount": amount,
                "balance": new_balance
            }

        except Exception:
            connection.rollback()
            raise

        finally:
            connection.close()
    def withdraw_money(self, customer_id, account_number, amount):
        if amount <= 0:
            raise InvalidAmountError(
                "Withdrawal amount must be greater than zero."
            )

        connection = create_connection()

        try:
            connection.start_transaction()

            account = self.account_repository.get_account_by_number_for_update(
                account_number, connection
            )

            if account is None:
                raise BankingError("Account not found.")

            if account[2] != customer_id:
                raise BankingError(
                    "You are not authorized to access this account."
                )

            if account[5] != "ACTIVE":
                raise InactiveAccountError("Account is not active.")

            if amount > account[4]:
                raise InsufficientBalanceError("Insufficient balance.")

            new_balance = account[4] - amount

            self.account_repository.update_balance(
                account_number, new_balance, connection
            )

            transaction_repository = TransactionRepository()

            transaction_id = transaction_repository.create_transaction_with_connection(
                from_account=account_number,
                to_account=None,
                transaction_type="WITHDRAW",
                amount=amount,
                status="SUCCESS",
                description="Cash Withdrawal",
                connection=connection
            )

            connection.commit()

            return {
                "message": "Money withdrawn successfully.",
                "transaction_id": transaction_id,
                "account_number": account_number,
                "amount": amount,
                "balance": new_balance
            }

        except Exception:
            connection.rollback()
            raise

        finally:
            connection.close() 

    def transfer_money(
        self,
        customer_id,
        from_account_number,
        to_account_number,
        amount,
        idempotency_key
    ):
        if not idempotency_key or len(idempotency_key) > 100:
            raise BankingError("A valid idempotency key is required.")

        if amount <= 0:
            raise InvalidAmountError(
                "Transfer amount must be greater than zero."
            )

        if from_account_number == to_account_number:
            raise BankingError(
                "Cannot transfer money to the same account."
            )

        request_data = {
            "from_account": from_account_number,
            "to_account": to_account_number,
            "amount": str(amount)
        }

        request_hash = hashlib.sha256(
            json.dumps(
                request_data,
                sort_keys=True
            ).encode("utf-8")
        ).hexdigest()

        connection = create_connection()

        try:
            connection.start_transaction()

            existing = self.idempotency_repository.get_by_customer_and_key(
                customer_id,
                idempotency_key,
                connection
            )

            if existing is not None:
                _, saved_hash, response_json, saved_status = existing

                if saved_hash != request_hash:
                    raise BankingError(
                        "This idempotency key was used for a different request."
                    )

                if saved_status == "COMPLETED" and response_json:
                    if isinstance(response_json, (bytes, bytearray)):
                        response_json = response_json.decode("utf-8")

                    connection.rollback()
                    return json.loads(response_json)

                raise BankingError(
                    "A request with this key is already being processed."
                )

            self.idempotency_repository.create_key(
                customer_id,
                idempotency_key,
                request_hash,
                connection
            )

            # Lock accounts in a consistent order.
            locked_accounts = {}

            for number in sorted([
                from_account_number,
                to_account_number
            ]):
                account = self.account_repository.get_account_by_number_for_update(
                    number,
                    connection
                )

                if account is None:
                    raise BankingError(f"Account {number} not found.")

                locked_accounts[number] = account

            from_account = locked_accounts[from_account_number]
            to_account = locked_accounts[to_account_number]

            if from_account[2] != customer_id:
                raise BankingError(
                    "You are not authorized to use this account."
                )

            if from_account[5] != "ACTIVE":
                raise InactiveAccountError(
                    "Sender account is not active."
                )

            if to_account[5] != "ACTIVE":
                raise InactiveAccountError(
                    "Receiver account is not active."
                )

            if amount > from_account[4]:
                raise InsufficientBalanceError(
                    "Insufficient balance."
                )

            sender_new_balance = from_account[4] - amount
            receiver_new_balance = to_account[4] + amount

            self.account_repository.update_balance(
                from_account_number,
                sender_new_balance,
                connection
            )

            self.account_repository.update_balance(
                to_account_number,
                receiver_new_balance,
                connection
            )

            transaction_repository = TransactionRepository()

            transaction_id = transaction_repository.create_transaction_with_connection(
                from_account=from_account_number,
                to_account=to_account_number,
                transaction_type="TRANSFER",
                amount=amount,
                status="SUCCESS",
                description="Fund Transfer",
                connection=connection
            )

            response = {
                "message": "Money transferred successfully.",
                "transaction_id": transaction_id,
                "from_account": from_account_number,
                "to_account": to_account_number,
                "amount": amount,
                "balance": sender_new_balance
            }

            self.idempotency_repository.complete_key(
                customer_id,
                idempotency_key,
                json.dumps(response, default=str),
                connection
            )

            connection.commit()
            return response

        except Exception:
            connection.rollback()
            raise

        finally:
            connection.close()

            
    def get_account_transactions(
        self,
        customer_id,
        account_number
    ):
        account = self.account_repository.get_account_by_number(
            account_number
        )

        if account is None:
            raise BankingError("Account not found.")

        if account[2] != customer_id:
            raise BankingError(
                "You are not authorized to access this account."
            )

        transaction_repository = TransactionRepository()

        transactions = (
            transaction_repository
            .get_transactions_by_account(account_number)
        )

        return [
            {
                "transaction_id": transaction[0],
                "from_account": transaction[1],
                "to_account": transaction[2],
                "transaction_type": transaction[3],
                "amount": transaction[4],
                "status": transaction[5],
                "description": transaction[6],
                "transaction_date": transaction[7]
            }
            for transaction in transactions
        ]


    def get_all_accounts(self):

        accounts = self.account_repository.get_all_accounts()

        return [
            {
                "account_id": account[0],
                "account_number": account[1],
                "customer_id": account[2],
                "account_type": account[3],
                "balance": account[4],
                "status": account[5],
                "created_at": account[6]
            }
            for account in accounts
        ]

    def get_all_transactions(self):

        transaction_repository = TransactionRepository()

        transactions = transaction_repository.get_all_transactions()

        return [
            {
                "transaction_id": transaction[0],
                "from_account": transaction[1],
                "to_account": transaction[2],
                "transaction_type": transaction[3],
                "amount": transaction[4],
                "status": transaction[5],
                "description": transaction[6],
                "transaction_date": transaction[7]
            }
            for transaction in transactions
        ]

    def update_account_status(self, account_number, status):

        account = self.account_repository.get_account_by_number(
            account_number
        )

        if account is None:
            raise BankingError("Account not found.")

        status = status.value  # Convert Enum to string

        allowed_statuses = [
            "ACTIVE",
            "BLOCKED"
        ]

        if status not in allowed_statuses:
            raise BankingError(
                "Invalid account status."
            )

        self.account_repository.update_account_status(
            account_number,
            status
        )

        return {
            "message": "Account status updated successfully.",
            "account_number": account_number,
            "status": status
        }

    def search_transactions(
    self,
    account_number=None,
    transaction_type=None,
    status=None
):

        transaction_repository = TransactionRepository()

        if transaction_type:
            transaction_type = transaction_type.upper()

        if status:
            status = status.upper()

        transactions = transaction_repository.search_transactions(
            account_number=account_number,
            transaction_type=transaction_type,
            status=status
        )

        return [
            {
                "transaction_id": transaction[0],
                "from_account": transaction[1],
                "to_account": transaction[2],
                "transaction_type": transaction[3],
                "amount": transaction[4],
                "status": transaction[5],
                "description": transaction[6],
                "transaction_date": transaction[7]
            }
            for transaction in transactions
        ]