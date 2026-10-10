from pydantic import BaseModel,Field
from datetime import date, datetime


class CustomerProfileResponse(BaseModel):
    customer_id: int
    name: str
    email: str
    phone: str
    address: str | None
    date_of_birth: date | None
    status: str
    created_at: datetime



class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8)
    confirm_password: str    

class UpdateProfileRequest(BaseModel):
    phone: str = Field(min_length=10, max_length=15)
    address: str = Field(min_length=1, max_length=255)
