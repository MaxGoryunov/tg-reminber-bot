from fastapi import FastAPI
import datetime
from bot import bot
from models import Notification, engine
from sqlalchemy.orm import Session
from sqlalchemy import update, insert, select, or_, delete, desc, and_
from utils import (
    offset_recurring_notification_by_interval,
    show_notification,
    mark_as_sent,
)
from logger import log_action, log_http_request


app = FastAPI()


def get_awaited_notifications_for_all():
    stmt = (
        select(Notification)
        # select(Notification.id, Notification.title, Notification.is_recurring)
        .where(or_(Notification.is_recurring == True, Notification.is_sent == False))
        .where(and_(Notification.notification_datetime <= datetime.datetime.now()))
        .order_by(Notification.notification_datetime)
    )
    with Session(engine) as session:
        res = session.execute(stmt, execution_options={"prebuffer_rows": True})
    return res.scalars().all()


def show_completed(nftn: Notification):
    bot.send_message(
        nftn.chat_id, "<b>You have a notification</b>: ", parse_mode="HTML"
    )
    msg = bot.send_message(nftn.chat_id, show_notification(nftn))


@app.get("/notify")
async def notify():
    awaited = get_awaited_notifications_for_all()
    log_http_request("notify", str(awaited))
    for nftn in awaited:
        if nftn.is_recurring:
            show_completed(nftn)
            offset_recurring_notification_by_interval(nftn)
        else:
            show_completed(nftn)
            mark_as_sent(nftn.id)
    return awaited
