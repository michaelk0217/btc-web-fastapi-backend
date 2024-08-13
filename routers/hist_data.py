from typing import Annotated
# from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio
from fastapi import Depends, HTTPException, Path, APIRouter
import yfinance as yf
import pandas as pd
from database import AsyncSessionLocal
from models import TickerData
from datetime import datetime
from starlette import status
from sqlalchemy.future import select

router = APIRouter()
#  hmm
# def get_db():
#      db = AsyncSessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

async def get_db():
    async with AsyncSessionLocal() as db:
        yield db

db_dependency = Annotated[AsyncSession, Depends(get_db)]

@router.get("/", status_code=status.HTTP_200_OK)
async def get_all_data(db: db_dependency):
    # return db.query(TickerData).all()
    # return await db.execute(db.query(TickerData)).scalars().all()
    result = await db.execute(select(TickerData))
    data = result.scalars().all()
    return data

@router.get("/by-interval/{itv}", status_code=status.HTTP_200_OK)
async def get_interval_data(db: db_dependency, itv: str = Path(min_length=2)):
    # data = db.query(TickerData).filter(TickerData.interval == itv).all()
    # result = await db.execute(db.query(TickerData).filter(TickerData.interval == itv))
    result = await db.execute(select(TickerData).filter(TickerData.interval == itv))
    data = result.scalars().all()

    if data:
        return data
    raise HTTPException(status_code=404, detail="Data not found")


# valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
# valid periods: “1d”, “5d”, “1mo”, “3mo”, “6mo”, “1y”, “2y”, “5y”, “10y”, “ytd”, “max”
@router.post("/post-data/{itv}", status_code=status.HTTP_201_CREATED)
async def create_hist_data(db: db_dependency, itv: str = Path(min_length=2)):
    ticker_symbol="BTC-USD"
    hist = await asyncio.to_thread(yf.Ticker(ticker_symbol).history, period="1mo", interval=itv)

    

    for index, row in hist.iterrows():
        existing_data = await db.execute(
            select(TickerData)
            .where(TickerData.ticker == ticker_symbol)
            .where(TickerData.interval == itv)
            .where(TickerData.date == index.to_pydatetime())
        )
        if not existing_data.scalar_one_or_none():
            ticker_data = TickerData(
                ticker=ticker_symbol,
                interval=itv,
                date=index.to_pydatetime(),
                open=row['Open'],
                high=row['High'],
                low=row['Low'],
                close=row['Close'],
                volume=row['Volume']
            )
            db.add(ticker_data)
    await db.commit()
