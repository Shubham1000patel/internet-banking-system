from pydantic import BaseModel, EmailStr
from datetime import date


class CustomerRegisterRequest(BaseModel):
    name: str
    email: EmailStr
    phone: str
    address: str
    date_of_birth: date
    password: str


class CustomerRegisterResponse(BaseModel):
    message: str
    customer_id: int