# from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import models
from database_url_private import URL 

# SQLALCHEMY_DATABASE_URL = 'sqlite:///./btc_data.db'
SQLALCHEMY_DATABASE_URL = URL


engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)

AsyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    class_=AsyncSession, 
    bind=engine
)

Base = declarative_base()

async def async_create_all(engine: AsyncEngine):
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
