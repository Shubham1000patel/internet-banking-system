from datetime import timezone,datetime

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from security import decode_access_token
from repositories.customer_repository import CustomerRepository

security = HTTPBearer()
customer_repository = CustomerRepository()


def get_current_customer(
    credentials: HTTPAuthorizationCredentials = Depends(security)   
):
    token = credentials.credentials

    try:
        payload = decode_access_token(token)

        customer_id = payload.get("customer_id")
        email = payload.get("email")
        issued_at = payload.get("iat")

        if customer_id is None or email is None or issued_at is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token."
            )

        customer = customer_repository.get_customer_by_id(customer_id)

        if customer is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Customer not found."
            )

        # Reject blocked or inactive customers.
        if customer[7] != "ACTIVE":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Customer account is not active."
            )

        # Check whether the token predates the password change.
        password_changed_at = customer_repository.get_password_changed_at(
            customer_id
        )

        if password_changed_at is not None:
            if password_changed_at.tzinfo is None:
                password_changed_at = password_changed_at.astimezone()

            if int(issued_at) < int(password_changed_at.timestamp()):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token expired because the password changed. Please log in again."
                )

        return {
            "customer_id": customer_id,
            "email": email
        }

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token."
        )