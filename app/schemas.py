from pydantic import BaseModel


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
