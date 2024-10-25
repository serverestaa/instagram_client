from fastapi import FastAPI
from db.database import engine
from db import models
from routers import user, post

app = FastAPI()

app.include_router(user.router)
app.include_router(post.router)
models.Base.metadata.create_all(engine)