from pydantic import BaseModel


class LoginRequest(BaseModel):
    login_id: str
    password: str


class LoginResponse(BaseModel):
    customer_id: int
    name: str
    email: str
    access_token: str
    token_type: str
    message: str