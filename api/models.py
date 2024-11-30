from pydantic import BaseModel
from typing import List
from flask_pydantic import validate

class Researcher(BaseModel):
    institution: str
    qualification: str
    verification: bool
    objective: str

class User(BaseModel):
    name: str
    pfp: str
    description: str
    USER_TYPE: str
    verification: bool
    gender: str
    age: int
    researcher: Researcher | None = None

class Comment(BaseModel):
    user: User
    content: str
    post_id: int

class Post(BaseModel):
    uid: User
    title: str
    content: str
    comments: List[Comment] = []
