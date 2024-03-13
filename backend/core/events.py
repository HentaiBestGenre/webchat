from typing import Callable
from fastapi import FastAPI

from backend.servises import ConnectionManger
from backend.db.repository import Repo


def create_start_app_handler(app: FastAPI) -> Callable:
    async def start_app() -> None:
        app.state.repository = Repo()
        app.state.manager = ConnectionManger()
    return start_app


def create_stop_app_handler(app: FastAPI) -> Callable:  # type: ignore
    async def stop_app() -> None:
        pass

    return stop_app
