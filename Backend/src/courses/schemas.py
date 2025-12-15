from pydantic import BaseModel
from datetime import datetime
import uuid
from typing import List


class Course(BaseModel):
    uid: uuid.UUID
    title: str
    sub_title: str
    description: str
    category: str
    level: str
    thumbnail: str
    language: str
    is_published: bool
    language: str
    user_uid: uuid.UUID
    created_at: datetime
    updated_at: datetime

class CourseCreateModel(BaseModel):
    title: str
    sub_title: str
    description: str
    category: str
    level: str
    thumbnail: str
    language: str
    is_published: bool
    language: str



class CourseUpdateModel(BaseModel):
    title: str
    sub_title: str
    description: str
    category: str
    level: str
    thumbnail: str
    language: str
    is_published: bool
    language: str