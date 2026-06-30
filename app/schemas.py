from pydantic import BaseModel, EmailStr


class PostBase(BaseModel):
    title: str
    content: str
    published: bool = False


class PostCreate(PostBase):
    pass


class Post(BaseModel):
    title: str
    content: str
    published: bool

    model_config = {"from_attributes": True}


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class User(BaseModel):
    email: EmailStr
    id: int
    model_config = {"from_attributes": True}


class UserLogin(BaseModel):
    email: EmailStr
    password: str
