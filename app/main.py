from fastapi import FastAPI
from .routers import post, user, auth, votes

app = FastAPI()

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(votes.router)


@app.get("/")
def root():
    return {"message": "Welcome to FastAPI Blog API"}
