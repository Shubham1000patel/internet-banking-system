from repositories.customer_repository import CustomerRepository
from exceptions import BankingError,ResourceConflictError
from security import hash_password,verify_password

class CustomerService:

    def __init__(self):
        self.customer_repository = CustomerRepository()

    def register_customer(
    self,
    name,
    email,
    phone,
    address,
    date_of_birth,
    password
):
        if self.customer_repository.email_exists(email):
            raise ResourceConflictError("Email already registered.")

        if self.customer_repository.phone_exists(phone):
            raise ResourceConflictError ("Phone number already registered.")

        if len(password) < 8:
            raise BankingError(
                "Password must contain at least 8 characters."
            )

        password_hash = hash_password(password)

        customer_id = self.customer_repository.create_customer(
            name=name,
            email=email,
            phone=phone,
            address=address,
            date_of_birth=date_of_birth,
            password_hash=password_hash
        )

        return customer_id

    def get_customer_profile(self, customer_id):

        customer = self.customer_repository.get_customer_by_id(
            customer_id
        )

        if customer is None:
            raise BankingError("Customer not found.")

        return {
            "customer_id": customer[0],
            "name": customer[1],
            "email": customer[2],
            "phone": customer[3],
            "address": customer[4],
            "date_of_birth": customer[5],
            "status": customer[7],
            "created_at": customer[8]
        }   
    


    def get_all_customers(self):

        customers = self.customer_repository.get_all_customers()

        return [
            {
                "customer_id": customer[0],
                "name": customer[1],
                "email": customer[2],
                "phone": customer[3],
                "address": customer[4],
                "date_of_birth": customer[5],
                "status": customer[6],
                "created_at": customer[7]
            }
            for customer in customers
        ]


    def update_customer_status(self, customer_id, status):

        customer = self.customer_repository.get_customer_by_id(
            customer_id
        )

        if customer is None:
            raise BankingError("Customer not found.")

        status = status.value  # Convert Enum to string

        allowed_statuses = [
            "ACTIVE",
            "BLOCKED"
        ]

        if status not in allowed_statuses:
            raise BankingError(
                "Invalid customer status."
            )

        self.customer_repository.update_customer_status(
            customer_id,
            status
        )

        return {
            "message": "Customer status updated successfully.",
            "customer_id": customer_id,
            "status": status
        }


    def change_password(
    self,
    customer_id,
    current_password,
    new_password,
    confirm_password
):
        # 1. Find the customer
        customer = self.customer_repository.get_customer_by_id(customer_id)

        if customer is None:
            raise BankingError("Customer not found.")

        # 2. Verify the current password
        if not verify_password(current_password, customer[6]):
            raise BankingError("Current password is incorrect.")

        # 3. Check the new password
        if len(new_password) < 8:
            raise BankingError(
                "New password must contain at least 8 characters."
            )

        # 4. Confirm both new passwords match
        if new_password != confirm_password:
            raise BankingError("New passwords do not match.")

        # 5. Prevent reusing the current password
        if verify_password(new_password, customer[6]):
            raise BankingError(
                "New password must differ from the current password."
            )

        # 6. Hash the new password
        password_hash = hash_password(new_password)

        # 7. Update the database
        self.customer_repository.update_password_hash(
            customer_id,
            password_hash
        )

        return {
            "message": "Password changed successfully."
        }    



    def update_profile(self, customer_id, phone, address):
    # 1. Check that the customer exists
        customer = self.customer_repository.get_customer_by_id(customer_id)

        if customer is None:
            raise BankingError("Customer not found.")

        # 2. Check whether another customer uses this phone
        if self.customer_repository.phone_exists_for_another_customer(
            phone, customer_id
        ):
            raise ResourceConflictError("Phone number already registered.")

        # 3. Update the profile
        self.customer_repository.update_customer_profile(
            customer_id=customer_id,
            phone=phone,
            address=address
        )

        # 4. Return the updated profile
        return self.get_customer_profile(customer_id)    