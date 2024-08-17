from fastapi import FastAPI
# import models
# import asyncio
from database import engine, async_create_all, AsyncSessionLocal
from routers import hist_data
from contextlib import asynccontextmanager
from routers.hist_data import initialize_base_data, initialize_base_data_TEST
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from scheduler import update_ticker_data
from apscheduler.triggers.interval import IntervalTrigger
from fastapi.middleware.cors import CORSMiddleware
# scheduler
update_data_scheduler = AsyncIOScheduler()
update_data_scheduler.add_job(update_ticker_data, IntervalTrigger(seconds=5))

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with AsyncSessionLocal() as db:
        # startup
        await async_create_all(engine)
        await initialize_base_data(db)
        # await initialize_base_data_TEST(db)
        update_data_scheduler.start()
        yield
        # shutdown
        update_data_scheduler.shutdown()

app = FastAPI(lifespan=lifespan)

app.include_router(hist_data.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
