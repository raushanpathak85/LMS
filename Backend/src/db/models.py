from sqlmodel import SQLModel, Field,Column,Relationship
import sqlalchemy.dialects.postgresql as pg
from typing import List,Optional
from datetime import datetime

import uuid

## Auth or user Table############
class User(SQLModel, table=True):
    __tablename__="users"

    uid: uuid.UUID =  Field(sa_column=Column(pg.UUID, nullable=False, primary_key=True,default=uuid.uuid4))
    username: str
    email: str
    first_name: str
    last_name: str
    role: str = Field(sa_column= Column(pg.VARCHAR,nullable=False,server_default='user'))
    is_verified: bool = Field(default=False)
    password_hash: str = Field(exclude=True)
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP,default=datetime.now))
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP,default=datetime.now))
    #courses: List['Course'] = Relationship(back_populates="user",sa_relationship_kwargs={'lazy':'selectin'})
    #reviews: List['Review'] = Relationship(back_populates="user",sa_relationship_kwargs={'lazy':'selectin'})



    def __repr__(self):
        return f"<User{self.username}>"
    



## Courses table##############
class Course(SQLModel,table=True):
    __tablename__ = "courses"

    uid: uuid.UUID = Field(sa_column=Column( pg.UUID,nullable=False,primary_key=True,default=uuid.uuid4))
    title: str
    sub_title: str
    description: str
    category: str
    level: str ## Beginner / Intermediate / Advanced
    thumbnail: str
    language: str
    is_published: bool
    user_uid: Optional[uuid.UUID] = Field(default= None, foreign_key= "users.uid")
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP,default=datetime.now))
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP,default=datetime.now))
    #user: Optional[User] = Relationship(back_populates= 'courses')
    #courses: List['Course'] = Relationship(back_populates="students",sa_relationship_kwargs={'lazy':'selectin'})
    ##student: Optional[Student] = Relationship(back_populates="course")
    #reviews: List['Review'] = Relationship(back_populates="course",sa_relationship_kwargs={'lazy':'selectin'})
    
    
    def __repr__(self):
        return f"<Course(title={self.title}>"

##Review Table######
class Review(SQLModel,table=True):
    __tablename__ = "reviews"

    uid: uuid.UUID = Field(sa_column=Column( pg.UUID,nullable=False,primary_key=True,default=uuid.uuid4))
    rating: int = Field(lt=5)
    review_text: str
    user_uid: Optional[uuid.UUID] = Field(default= None, foreign_key= "students.uid")
    course_uid: Optional[uuid.UUID] = Field(default= None, foreign_key= "courses.uid")
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP,default=datetime.now))
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP,default=datetime.now))
    #student: Optional[Student] = Relationship(back_populates="reviews")   
    #course: Optional[Course] = Relationship(back_populates="reviews")

    def __repr__(self):
        return f"<Review for book {self.book_uid} by user {self.user_uid}>"   


##Student Table####
class Student(SQLModel, table=True):
    __tablename__="students"

    uid: uuid.UUID =  Field(sa_column=Column(pg.UUID, nullable=False, primary_key=True,default=uuid.uuid4))
    username: str
    email: str
    first_name: str
    last_name: str
    role: str = Field(sa_column= Column(pg.VARCHAR,nullable=False,server_default='student'))
    is_verified: bool = Field(default=False)
    password_hash: str = Field(exclude=True)
    user_uid: Optional[uuid.UUID] = Field(default= None, foreign_key= "users.uid")
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP,default=datetime.now))
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP,default=datetime.now))
    #students: List['Student'] = Relationship(back_populates="courses",sa_relationship_kwargs={'lazy':'selectin'})
    #reviews: List['Review'] = Relationship(back_populates="user",sa_relationship_kwargs={'lazy':'selectin'})

    def __repr__(self):
        return f"<Student{self.username}>"