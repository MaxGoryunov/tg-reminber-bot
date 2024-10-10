import os
from sqlalchemy import Column, Integer, Boolean, DateTime, Time, Date, create_engine, String, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()

# db_uri = os.getenv('db_url')
db_uri = "postgresql://postgres:28Jun2003@host.docker.internal:5432/RpiLab"
engine = create_engine(db_uri, pool_size=10, max_overflow=20)

class Notification(Base):
    __tablename__ = 'notification'

    id = Column(Integer, primary_key=True)
    title = Column(String, default="def title")
    chat_id = Column(BigInteger, nullable=False)
    notification_datetime = Column(DateTime, nullable=False)  # Используем DateTime
    is_sent = Column(Boolean, default=False)
    is_recurring = Column(Boolean, default=False)
    day_interval = Column(Integer, default=7)
    last_sent_at = Column(DateTime)

    def __str__(self):
        res = f"{self.title}"
        if self.is_recurring:
            res = res + ", recurring notification"
        else:
            res = res + ", one-time notification"
        return res
