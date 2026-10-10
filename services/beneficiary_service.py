from repositories.beneficiary_repository import BeneficiaryRepository
from repositories.customer_repository import CustomerRepository
from exceptions import BankingError


class BeneficiaryService:

    def __init__(self):
        self.beneficiary_repository = BeneficiaryRepository()
        self.customer_repository = CustomerRepository()

    def add_beneficiary(
        self,
        customer_id,
        name,
        account_number,
        bank_name
    ):
        customer = self.customer_repository.get_customer_by_id(
            customer_id
        )

        if customer is None:
            raise BankingError("Customer not found.")

        if customer[7] != "ACTIVE":
            raise BankingError(
                "Customer is not active."
            )

        if not name.strip():
            raise BankingError(
                "Beneficiary name is required."
            )

        if not account_number.strip():
            raise BankingError(
                "Beneficiary account number is required."
            )

        if not bank_name.strip():
            raise BankingError(
                "Bank name is required."
            )

        beneficiary_id = (
            self.beneficiary_repository
            .create_beneficiary(
                customer_id=customer_id,
                name=name,
                account_number=account_number,
                bank_name=bank_name
            )
        )

        return {
            "message": "Beneficiary added successfully.",
            "beneficiary_id": beneficiary_id
        }

    def get_customer_beneficiaries(self, customer_id):

        customer = self.customer_repository.get_customer_by_id(
            customer_id
        )

        if customer is None:
            raise BankingError("Customer not found.")

        beneficiaries = (
            self.beneficiary_repository
            .get_beneficiaries_by_customer(customer_id)
        )

        return [
            {
                "beneficiary_id": beneficiary[0],
                "customer_id": beneficiary[1],
                "name": beneficiary[2],
                "account_number": beneficiary[3],
                "bank_name": beneficiary[4],
                "status": beneficiary[5],
                "created_at": beneficiary[6]
            }
            for beneficiary in beneficiaries
        ]

    def get_beneficiary(
        self,
        customer_id,
        beneficiary_id
    ):
        beneficiary = (
            self.beneficiary_repository
            .get_beneficiary_by_id(beneficiary_id)
        )

        if beneficiary is None:
            raise BankingError(
                "Beneficiary not found."
            )

        # Ownership check
        if beneficiary[1] != customer_id:
            raise BankingError(
                "You are not authorized to access this beneficiary."
            )

        return {
            "beneficiary_id": beneficiary[0],
            "customer_id": beneficiary[1],
            "name": beneficiary[2],
            "account_number": beneficiary[3],
            "bank_name": beneficiary[4],
            "status": beneficiary[5],
            "created_at": beneficiary[6]
        }

    def update_beneficiary(
        self,
        customer_id,
        beneficiary_id,
        name,
        account_number,
        bank_name
    ):
        beneficiary = (
            self.beneficiary_repository
            .get_beneficiary_by_id(beneficiary_id)
        )

        if beneficiary is None:
            raise BankingError(
                "Beneficiary not found."
            )

        # Ownership check
        if beneficiary[1] != customer_id:
            raise BankingError(
                "You are not authorized to update this beneficiary."
            )

        if not name.strip():
            raise BankingError(
                "Beneficiary name is required."
            )

        if not account_number.strip():
            raise BankingError(
                "Beneficiary account number is required."
            )

        if not bank_name.strip():
            raise BankingError(
                "Bank name is required."
            )

        self.beneficiary_repository.update_beneficiary(
            beneficiary_id=beneficiary_id,
            name=name,
            account_number=account_number,
            bank_name=bank_name
        )

        return {
            "message": "Beneficiary updated successfully."
        }

    def delete_beneficiary(
        self,
        customer_id,
        beneficiary_id
    ):
        beneficiary = (
            self.beneficiary_repository
            .get_beneficiary_by_id(beneficiary_id)
        )

        if beneficiary is None:
            raise BankingError(
                "Beneficiary not found."
            )

        # Ownership check
        if beneficiary[1] != customer_id:
            raise BankingError(
                "You are not authorized to delete this beneficiary."
            )

        self.beneficiary_repository.delete_beneficiary(
            beneficiary_id
        )

        return {
            "message": "Beneficiary deleted successfully."
        }