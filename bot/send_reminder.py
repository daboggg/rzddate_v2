import time
from datetime import date, datetime, timedelta

from aiogram.exceptions import TelegramBadRequest
from aiogram.utils.formatting import Bold, as_key_value, as_list, Italic

from bot.core import bot, scheduler
from bot.keyboards.done_keyboard import done_kb
from bot.utils.from_datetime_to_str import date_to_str


# фу
async def send_reminder(
        user_id: int,
        selected_date: date,
        selected_period: int,
        date_of_purchase: date,
        text: str,
        remind_me: bool,
        repeated_notification: int = 0,
        **kwargs
):
    if remind_me:

        format_text = as_list(
            Bold('💡 Не забудьте завтра купить билет!\n'),
            as_key_value('🚩 Дата поездки', date_to_str(selected_date)),
            as_key_value('🚩 Текст напоминания', text),
        ).as_html()

        message = await bot.send_message(user_id, format_text)

        today = datetime.now()
        scheduler.add_job(
            func=send_reminder,
            trigger='date',
            name=str(user_id),
            run_date=datetime(today.year, today.month, today.day, 7, 50) + timedelta(days=1),
            jobstore='sqlite',
            kwargs={
                'user_id': user_id,
                'selected_date': selected_date,
                'selected_period': selected_period,
                'date_of_purchase': date_of_purchase,
                'text': text,
                'remind_me': False,
                'message_id': message.message_id
            }
        )


    else:
        format_text = as_list(
            Bold('💡 Не забудьте сегодня купить билет!\n'),
            as_key_value('🚩 Дата поездки', date_to_str(selected_date)),
            as_key_value('🚩 Текст напоминания', text),
        ).as_html()

        if repeated_notification:
            format_text = Italic(f'повторное оповещение: {repeated_notification}').as_html() + format_text

        remind_id = str(time.time_ns())

        #  удалить предыдущее сообщение
        if msg_id := kwargs.get("message_id", None):
            try:
                await bot.delete_message(user_id, msg_id)
                # await msg.delete()
            except TelegramBadRequest:
                pass

        message = await bot.send_message(user_id, format_text, reply_markup=done_kb(remind_id))

        scheduler.add_job(
            id=remind_id,
            func=send_reminder,
            trigger='date',
            name=str(user_id),
            run_date=datetime.now() + timedelta(minutes=5),
            kwargs={
                'user_id': user_id,
                'selected_date': selected_date,
                'selected_period': selected_period,
                'date_of_purchase': date_of_purchase,
                'text': text,
                'remind_me': False,
                'repeated_notification': repeated_notification + 1,
                'message_id': message.message_id
            }
        )
