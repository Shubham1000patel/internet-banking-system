from repositories.transaction_repository import TransactionRepository
from repositories.account_repository import AccountRepository
from exceptions import (
    BankingError,
    AccountNotFoundError,
    InactiveAccountError,
    InvalidAmountError,
    InsufficientBalanceError,
    SameAccountTransferError
)
from database import create_connection


class TransactionService:

    def __init__(self):
        self.transaction_repository = TransactionRepository()
        self.account_repository = AccountRepository()

    def transfer_money(
        self,
        from_account_number,
        to_account_number,
        amount
    ):
        # 1. Validate amount
        if amount <= 0:
            raise InvalidAmountError(
                "Transfer amount must be greater than zero."
            )

        # 2. Prevent same-account transfer
        if from_account_number == to_account_number:
            raise SameAccountTransferError(
                "Cannot transfer money to the same account."
            )

        # 3. Find sender
        sender = self.account_repository.get_account_by_number(
            from_account_number
        )

        if sender is None:
            raise AccountNotFoundError(
                "Sender account not found."
            )

        # 4. Find receiver
        receiver = self.account_repository.get_account_by_number(
            to_account_number
        )

        if receiver is None:
            raise AccountNotFoundError(
                "Receiver account not found."
            )

        # accounts columns:
        # 0 account_id
        # 1 account_number
        # 2 customer_id
        # 3 account_type
        # 4 balance
        # 5 status
        # 6 created_at

        # 5. Check account status
        if sender[5] != "ACTIVE":
            raise InactiveAccountError(
                "Sender account is not active."
            )

        if receiver[5] != "ACTIVE":
            raise InactiveAccountError(
                "Receiver account is not active."
            )

        # 6. Check balance
        if amount > sender[4]:
            raise InsufficientBalanceError(
                "Insufficient balance."
            )

        # NOTE:
        # Actual balance update + transaction INSERT
        # will later be moved into one MySQL
        # transaction using COMMIT / ROLLBACK.

        return {
            "message": "Transfer validation successful.",
            "from_account": from_account_number,
            "to_account": to_account_number,
            "amount": amount
        }

    def get_transaction_history(self, account_number):

        account = self.account_repository.get_account_by_number(
            account_number
        )

        if account is None:
            raise AccountNotFoundError(
                "Account not found."
            )

        return self.transaction_repository.get_transactions_by_account(
            account_number
        )

    def transfer_money_real(
        self,
        from_account_number,
        to_account_number,
        amount
    ):
        connection = create_connection()

        try:
            # 1. Validate amount
            if amount <= 0:
                raise InvalidAmountError(
                    "Transfer amount must be greater than zero."
                )

            # 2. Same account check
            if from_account_number == to_account_number:
                raise SameAccountTransferError(
                    "Cannot transfer money to the same account."
                )

            # 3. Get accounts
            sender = self.account_repository.get_account_by_number(
                from_account_number
            )

            receiver = self.account_repository.get_account_by_number(
                to_account_number
            )

            if sender is None:
                raise AccountNotFoundError(
                    "Sender account not found."
                )

            if receiver is None:
                raise AccountNotFoundError(
                    "Receiver account not found."
                )

            # 4. Account status
            if sender[5] != "ACTIVE":
                raise InactiveAccountError(
                    "Sender account is not active."
                )

            if receiver[5] != "ACTIVE":
                raise InactiveAccountError(
                    "Receiver account is not active."
                )

            # 5. Balance check
            if amount > sender[4]:
                raise InsufficientBalanceError(
                    "Insufficient balance."
                )

            # 6. Calculate new balances
            sender_new_balance = sender[4] - amount
            receiver_new_balance = receiver[4] + amount

            # 7. Update sender
            self.account_repository.update_balance(
                from_account_number,
                sender_new_balance,
                connection
            )

            # 8. Update receiver
            self.account_repository.update_balance(
                to_account_number,
                receiver_new_balance,
                connection
            )

            # 9. Create transaction
            transaction_id = (
                self.transaction_repository
                .create_transaction_with_connection(
                    from_account=from_account_number,
                    to_account=to_account_number,
                    transaction_type="TRANSFER",
                    amount=amount,
                    status="SUCCESS",
                    description="Fund Transfer",
                    connection=connection
                )
            )

            # 10. Everything successful
            connection.commit()

            return {
                "message": "Transfer successful.",
                "transaction_id": transaction_id,
                "from_account": from_account_number,
                "to_account": to_account_number,
                "amount": amount
            }

        except Exception:
            # Something failed
            connection.rollback()
            raise

        finally:
            connection.close()    