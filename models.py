# from database import Base
from base import Base
from sqlalchemy import Column, DateTime, Integer, String, Double


class TickerData(Base):
    __tablename__='tickers'
    
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String)
    interval = Column(String)
    date = Column(DateTime(timezone=True))
    open = Column(Double)
    high = Column(Double)
    low = Column(Double)
    close = Column(Double)
    volume = Column(Double)