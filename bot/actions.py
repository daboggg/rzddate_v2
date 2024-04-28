from datetime import date, datetime, timedelta

from aiogram_dialog import DialogManager
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from bot.send_reminder import send_reminder


# добавляет напоминание в скедулер
def add_reminder(dialog_manager: DialogManager, remind_me: bool) -> None:
    apscheduler: AsyncIOScheduler = dialog_manager.middleware_data.get('apscheduler')

    selected_date = dialog_manager.dialog_data.get("selected_date")
    selected_period = dialog_manager.dialog_data.get("selected_period")
    date_of_purchase: date = dialog_manager.dialog_data.get('date_of_purchase')
    text = dialog_manager.dialog_data.get('text')

    if remind_me:
        rd = datetime(date_of_purchase.year, date_of_purchase.month, date_of_purchase.day, 8, 0) - timedelta(days=1)
        if rd < datetime.now():
            rd = datetime.now() + timedelta(minutes=2)
    else:
        rd = datetime(date_of_purchase.year, date_of_purchase.month, date_of_purchase.day, 7, 50)

    apscheduler.add_job(
        func=send_reminder,
        trigger='date',
        name=str(dialog_manager.event.from_user.id),
        run_date=rd,
        jobstore='sqlite',
        kwargs={
            'user_id': dialog_manager.event.from_user.id,
            'selected_date': selected_date,
            'selected_period': selected_period,
            'date_of_purchase': date_of_purchase,
            'text': text,
            'remind_me': remind_me
        }

    )
