class Customer:

    def __init__(self, customer_id, name, email, phone, address, password):
        self.customer_id = customer_id
        self.name = name
        self.email = email
        self.phone = phone
        self.address = address
        self.password = password
        self.status = "Active"  # Default status is "BLOCKED"
        self.is_logged_in = False
        self.beneficiaries = []
        self.accounts = []

    def view_profile(self):
        print("Customer ID:", self.customer_id)
        print("Name:", self.name)
        print("Email:", self.email)
        print("Phone:", self.phone)
        print("Address:", self.address)
        print("Status:", self.status)

    def update_profile(self,phone,address):
        self.phone = phone
        self.address = address

    def add_account(self, account):
        self.accounts.append(account)
        print(f"Account {account.account_number} linked successfully.")    

    def show_accounts(self):
        if not self.accounts:
            print("No accounts found.")
            return

        print("\n===== MY ACCOUNTS =====")

        for account in self.accounts:
            account.account_summary()

 
    def login(self,login_id,password) :
        if self.status !="ACTIVE":
            return False

        if (login_id == self.email or login_id == self.customer_id) and password == self.password:
            self.is_logged_in = True
            print("login Succesful.")
            return True
        print("Incorrect credentials.")
        return False
    def add_beneficiary(self, beneficiary):

        self.beneficiaries.append(beneficiary)

        print(
            f"Beneficiary {beneficiary.name} "
            f"added successfully."
        )


    def show_beneficiaries(self):

        if not self.beneficiaries:
            print("No beneficiaries found.")
            return

        print("\n===== MY BENEFICIARIES =====")

        for beneficiary in self.beneficiaries:
            beneficiary.show_beneficiary()    

    def logout(self):

        if self.is_logged_in:
            self.is_logged_in = False
            print("Logout successful.")
            return True

        print("Customer is not logged in.")
        return False

