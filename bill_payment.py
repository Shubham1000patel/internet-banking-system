from transaction import Transaction


class BillPayment:

    def __init__(self, bill_id, customer_id, account_number, amount):
        self.bill_id = bill_id
        self.customer_id = customer_id
        self.account_number = account_number
        self.amount = amount
        self.status = "PENDING"

    def pay(self, account):

        if self.amount <= 0:
            print("Bill amount must be greater than zero.")
            self.status = "FAILED"
            return False

        if self.amount > account.check_balance():
            print("Insufficient balance.")
            self.status = "FAILED"
            return False

        if not account.deduct_balance(self.amount):
            print("Bill payment failed.")
            self.status = "FAILED"
            return False

        transaction = Transaction(
            transaction_id=f"TXN{len(account.transactions) + 1:03d}",
            transaction_type="BILL_PAYMENT",
            amount=self.amount,
            from_account=account.account_number,
            description="Bill Payment"
        )

        transaction.mark_success()

        account.transactions.append(transaction)

        self.status = "SUCCESS"

        print(f"₹{self.amount} bill paid successfully.")

        return True

    def show_bill(self):
        print("\n----- BILL PAYMENT -----")
        print("Bill ID       :", self.bill_id)
        print("Customer ID   :", self.customer_id)
        print("Account       :", self.account_number)
        print("Amount        :", f"₹{self.amount}")
        print("Status        :", self.status)

class ElectricityBill(BillPayment):

    def __init__(
        self,
        bill_id,
        customer_id,
        account_number,
        amount,
        units
    ):
        super().__init__(
            bill_id,
            customer_id,
            account_number,
            amount
        )

        self.units = units

    def show_bill(self):
        print("\n----- ELECTRICITY BILL -----")
        print("Bill ID       :", self.bill_id)
        print("Customer ID   :", self.customer_id)
        print("Account       :", self.account_number)
        print("Units         :", self.units)
        print("Amount        :", f"₹{self.amount}")
        print("Status        :", self.status)

class MobileBill(BillPayment):

    def __init__(
        self,
        bill_id,
        customer_id,
        account_number,
        amount,
        mobile_number
    ):
        super().__init__(
            bill_id,
            customer_id,
            account_number,
            amount
        )

        self.mobile_number = mobile_number

    def show_bill(self):
        print("\n----- MOBILE BILL -----")
        print("Bill ID       :", self.bill_id)
        print("Customer ID   :", self.customer_id)
        print("Account       :", self.account_number)
        print("Mobile Number :", self.mobile_number)
        print("Amount        :", f"₹{self.amount}")
        print("Status        :", self.status)                