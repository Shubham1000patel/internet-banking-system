from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from security import decode_access_token
from repositories.admin_repository import AdminRepository

security = HTTPBearer()
admin_repository = AdminRepository()


def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials

    try:
        payload = decode_access_token(token)

        admin_id = payload.get("admin_id")
        email = payload.get("email")
        role = payload.get("role")

        if admin_id is None or email is None or role is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid admin token."
            )

        admin = admin_repository.get_admin_by_id(admin_id)

        if admin is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Admin account not found."
            )

        # Check the latest database status.
        if admin[5] != "ACTIVE":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin account is not active."
            )

        # Check that token claims still match the database.
        if admin[2] != email or admin[4] != role:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Admin token is no longer valid."
            )

        if role != "ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required."
            )

        return {
            "admin_id": admin[0],
            "email": admin[2],
            "role": admin[4]
        }

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired admin token."
        )