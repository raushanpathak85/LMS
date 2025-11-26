
from sqlmodel import SQLModel,Field,Column,Relationship
from src.auth import models
import sqlalchemy.dialects.postgresql as pg
from datetime import datetime,date
from typing import Optional
import uuid

class Book(SQLModel,table=True):
    __tablename__ = "books"

    uid: uuid.UUID = Field(sa_column=Column( pg.UUID,nullable=False,primary_key=True,default=uuid.uuid4))
    title: str
    author: str
    publisher: str
    published_date: str 
    page_count: int
    language: str
    user_uid: Optional[uuid.UUID] = Field(default= None, foreign_key= "users.uid")
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP,default=datetime.now))
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP,default=datetime.now))
    user: Optional['models.User'] = Relationship(back_populates="books")
    
    
    def __repr__(self):
        return f"<Book(title={self.title}>"
        