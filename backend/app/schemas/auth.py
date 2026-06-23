from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    success: bool
    admin_id: Optional[int] = None
    username: Optional[str] = None
    access_token: Optional[str] = None
    message: str = ""