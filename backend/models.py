from pydantic import BaseModel, Field, validator
from typing import Optional, Union


class UserInDB(BaseModel):
    username: str
    hashed_password: str
    id : int


class LoginUser(BaseModel):
    username: str
    password: str


class RegisterUser(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    confirmation_password: str = Field(..., min_length=6)

    @validator('confirmation_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v

class RegisterRequest(BaseModel):
    user: RegisterUser

class LoginRequest(BaseModel):
    user: LoginUser


class SendMessage(BaseModel):
    user_id: int
    content: str


class DeleteMessageModel(BaseModel):
    user_id: int


class UpdateMessageModel(BaseModel):
    user_id: int
    content: str
