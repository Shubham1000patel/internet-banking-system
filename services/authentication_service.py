
from repositories.customer_repository import CustomerRepository
from exceptions import BankingError
from security import verify_password, create_access_token


class AuthenticationService:

    def __init__(self):
        self.customer_repository = CustomerRepository()

    def login(self, login_id, password):
        customer = None

        # Try customer ID first.
        if login_id.isdigit():
            customer = self.customer_repository.get_customer_by_id(
                int(login_id)
            )

        # If no customer ID match, try email.
        if customer is None:
            customer = self.customer_repository.get_customer_by_email(
                login_id
            )

        # Use a generic message when the customer doesn't exist.
        if customer is None:
            raise BankingError("Incorrect credentials.")

        # Verify that the customer account is active.
        if customer[7] != "ACTIVE":
            raise BankingError("Customer account is not active.")

        # Verify the submitted password against the stored bcrypt hash.
        if not verify_password(password, customer[6]):
            raise BankingError("Incorrect credentials.")

        # Create an access token after successful authentication.
        access_token = create_access_token(
            customer_id=customer[0],
            email=customer[2]
        )

        return {
            "customer_id": customer[0],
            "name": customer[1],
            "email": customer[2],
            "access_token": access_token,
            "token_type": "bearer",
            "message": "Login successful."
        }