from transaction import Transaction
from exceptions import InvalidAmountError, InsufficientBalanceError,InactiveAccountError, AccountNotFoundError, SameAccountTransferError
class Account:

    def __init__(
        self,
        account_id,
        account_number,
        customer_id,
        account_type,
        initial_balance=0
    ):
        self.account_id = account_id
        self.account_number = account_number
        self.customer_id = customer_id
        self.account_type = account_type
        self.__balance = initial_balance
        self.status = "ACTIVE"  # Default status is "BLOCKED"
        self.transactions = [] 

    def check_balance(self):
     return self.__balance    

    def deposit(self, amount):

        if self.status != "ACTIVE":
            raise InactiveAccountError(
                "Cannot deposit money to an inactive account."
            )   

        if amount <= 0:
            raise InvalidAmountError(
            "Withdrawal amount must be greater than zero."
        )

        if amount > self.__balance:
            raise InsufficientBalanceError(
            "Insufficient balance."
        )

        self.__balance += amount

        transaction = Transaction(
            transaction_id=f"TXN{len(self.transactions) + 1:03d}",
            transaction_type="DEPOSIT",
            amount=amount,
            to_account=self.account_number,
            description="Money deposited"
        )

        transaction.mark_success()

        self.transactions.append(transaction)

        print(f"₹{amount} deposited successfully.")

        return True
    def withdraw(self, amount):
        if self.status != "ACTIVE":
            raise InactiveAccountError(
                "Cannot withdraw money from an inactive account."
            )

        if amount <= 0:
            print("Withdrawal amount must be greater than zero.")
            return False

        if amount > self.__balance:
            print("Insufficient balance.")
            return False

        self.__balance -= amount

        transaction = Transaction(
                        transaction_id=f"TXN{len(self.transactions) + 1:03d}",
                        transaction_type="Wthdraw",
                        amount=amount,
                        from_account=self.account_number,
                        description="Money Withdrawn"
                )
        transaction.mark_success()
        self.transactions.append(transaction)

        print(f"₹{amount} withdrawn successfully.")
        return True

    def deduct_balance(self, amount):

        if amount <= 0:
            raise InvalidAmountError(
                "Amount must be greater than zero."
            )

        if amount > self.__balance:
            raise InsufficientBalanceError(
                "Insufficient balance."
            )

        self.__balance -= amount

        return True

    def add_balance(self, amount):

        if amount <= 0:
            raise InvalidAmountError(
                "Amount must be greater than zero."
            )

        self.__balance += amount    

        return True
    def account_summary(self):
        print(f"Account ID : {self.account_id} ")
        print(f"Account number :{self.account_number}")
        print(f"Customer ID : {self.customer_id}")
        print(f"Account Type :{self.account_type}")
        print(f"Balance : {self.__balance}")
        print(f"Status : {self.status}")

    def show_transactions(self):

        if not self.transactions:
            print("No transactions found.")
            return

        print("\n===== TRANSACTION HISTORY =====")

        for transaction in self.transactions:
            transaction.show_transaction()
        