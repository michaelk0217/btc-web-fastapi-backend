from fastapi import FastAPI
import models
import asyncio
from database import engine, async_create_all
from routers import hist_data
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    await async_create_all(engine)
    yield
    # shutdown

app = FastAPI(lifespan=lifespan)

# @app.on_event("startup")
# async def on_startup():
#     await async_create_all(engine)

app.include_router(hist_data.router)
