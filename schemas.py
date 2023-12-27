from typing import Optional
import pydantic as _pydantic


class UserBase(_pydantic.BaseModel):
    email: str


class UserCreate(UserBase):
    hashed_password: str

    class Config:
        from_attributes = True   


class User(UserBase):
    id: int

    class Config:
        from_attributes = True   
