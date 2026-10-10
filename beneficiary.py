class Beneficiary:

    def __init__(self, beneficiary_id, name, account_number, bank_name):
        self.beneficiary_id = beneficiary_id
        self.name = name
        self.account_number = account_number
        self.bank_name = bank_name
        self.status = "ACTIVE"


    def show_beneficiary(self):

        print("\n----- BENEFICIARY DETAILS -----")
        print("Beneficiary ID :", self.beneficiary_id)
        print("Name           :", self.name)
        print("Account Number :", self.account_number)
        print("Bank Name      :", self.bank_name)
        print("Status         :", self.status)
            