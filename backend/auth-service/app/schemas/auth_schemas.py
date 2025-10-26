from pydantic import BaseModel, EmailStr
from typing import Optional

class UserOut(BaseModel):
    user_id: str
    email: EmailStr
    full_name: str
    kyc_status: str

    class Config:
        from_attributes = True
