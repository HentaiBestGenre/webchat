from fastapi import WebSocket
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta
from typing import Optional


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password: str):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, "SECRET_KEY", algorithm="HS256")
    return encoded_jwt


class ConnectionManger:
    def __init__(self) -> None:
        self.connection = []
        
    def add(self, connection: WebSocket):
        self.connection.append(connection)
    
    async def remove(self, websocket: WebSocket):
        if websocket in self.connection:
            self.connection.remove(websocket)
            await websocket.close()

    async def broadcast(self, type, data):
        for i in self.connection:
            await i.send_json({
                "message": {
                    "type": type,
                    "data": data
                }
            })
