from transaction import Transaction


class Bank:

    def __init__(self):
        self.customers = []
        self.accounts = []
        self.transactions = []

    def add_account(self, account):
        self.accounts.append(account)

    def find_account(self, account_number):

        for account in self.accounts:

            if account.account_number == account_number:
                return account

        return None

    def transfer_money(self, from_account_number, to_account_number, amount):

        # 1. Find sender account
        from_account = self.find_account(from_account_number)

        # 2. Find receiver account
        to_account = self.find_account(to_account_number)

        # 3. Check sender account
        if from_account is None:
            print("Sender account not found.")
            return False

        # 4. Check receiver account
        if to_account is None:
            print("Receiver account not found.")
            return False

        # 5. Don't allow transfer to the same account
        if from_account.account_number == to_account.account_number:
            print("Cannot transfer money to the same account.")
            return False

        # 6. Check sender status
        if from_account.status != "ACTIVE":
            print("Sender account is not active.")
            return False

        # 7. Check receiver status
        if to_account.status != "ACTIVE":
            print("Receiver account is not active.")
            return False

        # 8. Validate amount
        if amount <= 0:
            print("Transfer amount must be greater than zero.")
            return False

        # 9. Check sender balance
        if amount > from_account.check_balance():
            print("Insufficient balance.")
            return False

        # 10. Deduct money from sender
        if not from_account.deduct_balance(amount):
            print("Transfer failed.")
            return False

        # 11. Add money to receiver
        if not to_account.add_balance(amount):

            # Rollback sender balance
            from_account.add_balance(amount)

            print("Transfer failed.")
            return False

        # 12. Create transfer transaction
        transaction = Transaction(
            transaction_id=f"TXN{len(self.transactions) + 1:03d}",
            transaction_type="TRANSFER",
            amount=amount,
            from_account=from_account.account_number,
            to_account=to_account.account_number,
            description="Fund Transfer"
        )

        # 13. Mark transaction successful
        transaction.mark_success()

        # 14. Store transaction
        self.transactions.append(transaction)

        from_account.transactions.append(transaction)
        to_account.transactions.append(transaction)

        print(f"₹{amount} transferred successfully.")

        return True