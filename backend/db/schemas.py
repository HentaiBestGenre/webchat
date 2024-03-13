from typing import List
from sqlalchemy import ForeignKey, String, TIMESTAMP
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import datetime


class Base(DeclarativeBase):
    type_annotation_map = {
        datetime.datetime: TIMESTAMP(timezone=True),
    }


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(100), nullable=False)

    messages: Mapped[List["Messages"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class Messages(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str]
    user_name: Mapped[str] = mapped_column(String(50))
    created_at: Mapped[datetime.datetime]

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="messages")

    def __repr__(self) -> str:
        return f"Message(id={self.id!r}, content={self.content!r})"

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'content': self.content,
            'user_name': self.user_name,
            'created_at': self.created_at.strftime("%H:%M") if self.created_at else None
        }
    

if __name__ == "__main__":
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    DATABASE_URL = "postgresql+psycopg2://postgres:yourpassword@localhost/Test"

    engine = create_engine(DATABASE_URL)
    Base.metadata.bind = engine

    Session = sessionmaker(bind=engine)

    Base.metadata.create_all(engine)
