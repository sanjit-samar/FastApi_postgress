from typing import Optional
from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
import psycopg2
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel
from random import randrange

app = FastAPI()


class Post(BaseModel):
    title: str
    content: str
    published: bool = False
    rating: Optional[int] = None


try:
    conn = psycopg2.connect(
        host="localhost",
        database="fastApi",
        user="postgres",
        password="Sanjit@08",
        cursor_factory=RealDictCursor,
    )
    cursor = conn.cursor()
    print("connection Success")
except Exception as error:
    print("Error while connecting database -", error)


# Simulated database (in-memory storage)
my_posts = [
    {
        "id": 1,
        "title": "First Post",
        "content": "Content of first post",
        "published": True,
    },
    {
        "id": 2,
        "title": "Second Post",
        "content": "Content of second post",
        "published": False,
    },
]


@app.get("/")
def root():
    return {"message": "Welcome to FastAPI Blog API"}


@app.get("/posts")
def get_posts():
    """Get all posts"""
    cursor.execute(""" SELECT * FROM posts """)
    posts = cursor.fetchall()
    print("data", posts)
    return posts


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(post: Post):
    """Create a new post"""
    cursor.execute(
        """ INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """,
        (post.title, post.content, post.published),
    )

    new_post = cursor.fetchone()
    conn.commit()
    return {"new_post": new_post}


@app.get("/posts/{id}")
def get_post(id: int):
    """Get a single post by ID"""
    cursor.execute(""" SELECT * from posts WHERE id = %s """, (str(id)))
    post = cursor.fetchone()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} not found"
        )
    return post


@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    """Update a post by ID"""
    cursor.execute(
        """UPDATE posts SET title = %s, content= %s, published= %s WHERE id = %s RETURNING * """,
        (post.title, post.content, post.published, id),
    )
    post_updated = cursor.fetchone()
    conn.commit()
    if post_updated is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} not found"
        )
    return {"msg": post_updated}


@app.delete("/posts/{id}", status_code=status.HTTP_200_OK)
def delete_post(id: int):
    """Delete a post by ID"""
    cursor.execute(
        """ DELETE FROM posts WHERE id = %s RETURNING * """,
        (
            str(
                id,
            ),
        ),
    )
    delete_post = cursor.fetchone()
    conn.commit()
    if delete_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} not found"
        )
    # return Response(status_code=status.HTTP_204_NO_CONTENT)
    return {"message": "Post deleted successfully"}
