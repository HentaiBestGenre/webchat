from pydantic import BaseModel
from typing import Optional, Union


class UserInDB(BaseModel):
    username: str
    hashed_password: str
    id : int


class LoginUser(BaseModel):
    username: str
    password: str


class RegisterUser(BaseModel):
    username: str
    password: str
    confirmation_password: str


class AuthRequest(BaseModel):
    user: Union[RegisterUser, LoginUser]


class SendMessage(BaseModel):
    user_id: int
    content: str


class DeleteMessageModel(BaseModel):
    user_id: int


class UpdateMessageModel(BaseModel):
    user_id: int
    content: str
