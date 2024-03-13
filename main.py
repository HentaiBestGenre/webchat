from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fastapi import HTTPException, Depends, WebSocket
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.repository import Repo
from backend.servises import verify_password, create_access_token, ConnectionManger
from backend.dependencies import get_repository, get_session, get_repository_ws, get_manager, get_manager_ws
from backend.models import (
    AuthRequest,
    LoginUser,
    RegisterUser,
    SendMessage,
    DeleteMessageModel,
    UpdateMessageModel
)



@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.repository = Repo()
    app.state.manager = ConnectionManger()
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
    

@app.post("/login")
async def login(
    user: AuthRequest,
    session: AsyncSession = Depends(get_session),
    repository: Repo = Depends(get_repository)
):
    user: LoginUser = user.user

    user_db = await repository.get_user_by_username(session, user.username)
    if not user_db or not verify_password(user.password, user_db.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    data = {"username": user_db.username, "id": user_db.id}
    return {"user": data, "token": create_access_token(data)}


@app.post("/register")
async def login(
    user: AuthRequest,
    session: AsyncSession = Depends(get_session),
    repository: Repo = Depends(get_repository)
):
    user: RegisterUser = user.user
    if user.password != user.confirmation_password:
        raise HTTPException(status_code=400, detail="Password is not equal")

    users_db = await repository.get_user_by_username(session, user.username)
    if users_db:
        print(users_db)
        raise HTTPException(status_code=400, detail="Username already registered")
    user = await repository.create_user(session, user.username, user.password)
    return {"username": user.username, "message": "User successfully registered"}


@app.post("/messages")
async def messages(
    message: SendMessage,
    session: AsyncSession = Depends(get_session),
    repository: Repo = Depends(get_repository),
    manager: ConnectionManger = Depends(get_manager)
):
    user = await repository.get_user(session, message.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    message = await repository.add_messages(
        session, 
        user_id = message.user_id,
        content = message.content,
        user_name = user.username
    )
    await manager.broadcast("create", message.to_dict())
    return message.to_dict()


@app.delete("/messages/{message_id}")
async def messages(
    message_id: int, 
    data: DeleteMessageModel,
    session: AsyncSession = Depends(get_session),
    repository: Repo = Depends(get_repository),
    manager: ConnectionManger = Depends(get_manager)
):
    
    await repository.delete_message(session, message_id)
    messages = await repository.get_messages(session)
    messages = [i._asdict()['Messages'].to_dict() for i in messages]
    await manager.broadcast("destroy", messages)
    return {}


@app.patch("/messages/{message_id}")
async def messages(
    message_id: int, 
    data: UpdateMessageModel,
    session: AsyncSession = Depends(get_session),
    repository: Repo= Depends(get_repository),
    manager: ConnectionManger = Depends(get_manager)
):
    await repository.update_message(session, message_id, data.content)
    messages = await repository.get_messages(session)
    messages = [i._asdict()['Messages'].to_dict() for i in messages]
    await manager.broadcast("update", messages)
    return {}


@app.websocket("/cable")
async def websocket_endpoint(
    websocket: WebSocket,
    session: AsyncSession = Depends(get_session),
    repository: Repo = Depends(get_repository_ws),
    manager: ConnectionManger = Depends(get_manager_ws)
):
    try:
        await websocket.accept()
        manager.add(websocket)
        chat_history = await repository.get_messages(session)
        print([i._asdict()['Messages'].to_dict() for i in chat_history])
        await websocket.send_json({
            "message": {
                "type": "connection",
                "data": [i._asdict()['Messages'].to_dict() for i in chat_history]
            }
        })

        while True:
            data = await websocket.receive_json()
            print(data)
    except Exception as e:
        print("Error in websocket:", e)
        await manager.remove(websocket)
        return HTTPException(status_code=500, detail="Error in websocket")
    