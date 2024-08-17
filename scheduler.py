import asyncio
# from apscheduler.schedulers.asyncio import AsyncIOScheduler
import yfinance as yf
from database import AsyncSessionLocal
from models import TickerData
from sqlalchemy.future import select
# from sqlalchemy.ext.asyncio import AsyncSession
# from fastapi import Depends
from datetime import datetime, timedelta, timezone
from routers.hist_data import db_dependency

# async def update_current_price():
#     ticker_symbol="BTC-USD"
#     current_price = yf.Ticker(ticker_symbol).history(period='1d')['Close'].iloc[-1]


async def update_ticker_data():
    ticker_symbol = "BTC-USD"
    intervals = ["1d", "1h", "15m", "5m"]
    intervals_to_min = {"1d": 1440, "1h": 60, "15m": 15, "5m": 5}

    async with AsyncSessionLocal() as db:
        current = await asyncio.to_thread(lambda: yf.Ticker(ticker_symbol).history(period="1d", interval="1m").iloc[-1])
        current_price = current['Close']
        current_vol = current['Volume']
        for itv in intervals:
            # Fetch the latest data from Yahoo Finance for the specific interval
            hist = await asyncio.to_thread(yf.Ticker(ticker_symbol).history, period="1d", interval=itv)
            most_recent_row = hist.iloc[-1]
            most_recent_time = most_recent_row.name.to_pydatetime().astimezone(timezone.utc)

            # Check if the last stored ticker data is still open
            existing_data = await db.execute(
                select(TickerData)
                .where(TickerData.ticker == ticker_symbol)
                .where(TickerData.interval == itv)
                .order_by(TickerData.date.desc())
                .limit(1)
            )
            latest_ticker = existing_data.scalar_one_or_none()

            if latest_ticker:
                # If the ticker is still open (less than interval period since last update)
                # if (datetime.now(timezone.utc) - latest_ticker.date) < timedelta(minutes=intervals_to_min[itv])
                if (most_recent_time - latest_ticker.date) < timedelta(minutes=intervals_to_min[itv]):
                    latest_ticker.close = current_price
                    latest_ticker.volume = current_vol
                    db.add(latest_ticker)
                else:
                    # If the latest data has moved to a new interval
                    if most_recent_time > latest_ticker.date:
                        ticker_data = TickerData(
                            ticker=ticker_symbol,
                            interval=itv,
                            date=most_recent_time,
                            open=most_recent_row['Open'],
                            high=most_recent_row['High'],
                            low=most_recent_row['Low'],
                            close=most_recent_row['Close'],
                            volume=most_recent_row['Volume']
                        )
                        db.add(ticker_data)
        await db.commit()
        
        print("\nCURRENT BITCOIN PRICE")
        print("***********************")
        print(current_price)
        print(datetime.now(timezone.utc))
        print("***********************")


    


