from fastapi import FastAPI
import models
import asyncio
from database import engine, async_create_all
from routers import hist_data
from contextlib import asynccontextmanager


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     await async_create_all(engine)



# models.Base.metadata.create_all(bind=engine)

# @app.on_event("startup")
# async def on_startup():
#     await init_db()

# async def init_db():
#     async with engine.begin() as conn:
#         await conn.run_sync(models.Base.metadata.create_all)


app = FastAPI()

@app.on_event("startup")
async def on_startup():
    await async_create_all(engine)

app.include_router(hist_data.router)
