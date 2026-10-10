from datetime import datetime


class Transaction:

    def __init__(
        self,
        transaction_id,
        transaction_type,
        amount,
        from_account=None,
        to_account=None,
        description=""
    ):
        self.transaction_id = transaction_id
        self.transaction_type = transaction_type
        self.amount = amount
        self.from_account = from_account
        self.to_account = to_account
        self.status = "PENDING"
        self.date = datetime.now()
        self.description = description

    def mark_success(self):
        self.status = "SUCCESS"    

    def mark_failed(self):
        self.status = "FAILED"

    def show_transaction(self):

        print("\n----- TRANSACTION DETAILS -----")
        print("Transaction ID :", self.transaction_id)
        print("Type           :", self.transaction_type)
        print("Amount         :", f"₹{self.amount}")
        print("From Account   :", self.from_account)
        print("To Account     :", self.to_account)
        print("Status         :", self.status)
        print("Date           :", self.date)
        print("Description    :", self.description)        