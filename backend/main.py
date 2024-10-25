from fastapi import FastAPI

from auth import authentication
from db.database import engine
from db import models
from routers import user, post, comment
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.include_router(authentication.router)
app.include_router(user.router)
app.include_router(post.router)
app.include_router(comment.router)
models.Base.metadata.create_all(engine)

app.mount('/images', StaticFiles(directory='images'), name='images')
