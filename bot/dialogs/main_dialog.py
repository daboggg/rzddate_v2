from datetime import date, timedelta
from typing import Any

from aiogram import F
from aiogram.enums import ContentType
from aiogram.types import CallbackQuery, Message
from aiogram.utils.formatting import Bold, Italic, as_key_value
from aiogram_dialog import Dialog, Window, DialogManager, StartMode, ShowMode
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Row, Back, CalendarConfig, Start, SwitchTo
from aiogram_dialog.widgets.text import Const, Format

from bot.actions import add_reminder
from bot.dialogs.utils import CustomCalendar
from bot.state_groups import MainDialogSG
from bot.utils.converter import conv_voice
from bot.utils.from_datetime_to_str import date_to_str


async def getter_period(dialog_manager: DialogManager, **kwargs) -> dict[str, Any]:
    return {
        'selected_date': date_to_str(dialog_manager.dialog_data.get("selected_date")),
    }


async def getter_date_of_purchase(dialog_manager: DialogManager, **kwargs) -> dict[str, Any]:
    selected_date = dialog_manager.dialog_data.get("selected_date")
    selected_period = dialog_manager.dialog_data.get("selected_period")
    date_of_purchase = selected_date - timedelta(days=selected_period - 1)
    dialog_manager.dialog_data['date_of_purchase'] = date_of_purchase

    return {
        'selected_date': date_to_str(selected_date),
        'selected_period': selected_period,
        'date_of_purchase': date_to_str(date_of_purchase) if date_of_purchase > date.today() else 'Продажа уже открыта',
        'show_buttons': True if date_of_purchase > date.today() else False
    }


async def getter_remind_me(dialog_manager: DialogManager, **kwargs) -> dict[str, Any]:
    # apscheduler: AsyncIOScheduler = dialog_manager.middleware_data.get('apscheduler')
    selected_date = dialog_manager.dialog_data.get("selected_date")
    selected_period = dialog_manager.dialog_data.get("selected_period")
    date_of_purchase = dialog_manager.dialog_data.get('date_of_purchase')
    text = dialog_manager.dialog_data.get('text')
    return {
        'selected_date': date_to_str(selected_date),
        'selected_period': selected_period,
        'date_of_purchase': date_to_str(date_of_purchase),
        "text": text
    }


# #########################################################################


async def on_date_selected(callback: CallbackQuery, widget,
                           manager: DialogManager, selected_date: date) -> None:
    manager.dialog_data["selected_date"] = selected_date
    await manager.switch_to(MainDialogSG.get_period)


async def on_period_selected(callback: CallbackQuery, button: Button,
                             manager: DialogManager) -> None:
    manager.dialog_data["selected_period"] = int(button.widget_id)
    await manager.switch_to(MainDialogSG.get_date_of_purchase)


async def text_handler(message: Message, message_input: MessageInput, manager: DialogManager) -> None:
    manager.show_mode = ShowMode.DELETE_AND_SEND
    try:
        if message.text:
            text = message.text
        else:
            text = await conv_voice(message, message.bot)
        manager.dialog_data['text'] = text
        await manager.switch_to(MainDialogSG.remind_me)
    except:
        await manager.switch_to(MainDialogSG.get_text_or_voice)


async def remind_me_selected(callback: CallbackQuery, button: Button,
                             manager: DialogManager) -> None:
    remind_me = True if button.widget_id == 'yes' else False
    add_reminder(manager, remind_me)
    await manager.switch_to(MainDialogSG.finish)


#############################################################################
main_dialog = Dialog(
    Window(
        Const(Bold("🚂 Выберите дату поездки").as_html()),
        CustomCalendar(
            id='calendar',
            on_click=on_date_selected,
            config=CalendarConfig(min_date=date.today())
        ),
        state=MainDialogSG.start
    ),
    Window(
        Format(as_key_value("🚩 Дата поездки", "{selected_date}\n").as_html()),
        Const(Italic("〰️ Выберите период (за сколько дней открывается продажа)").as_html()),

        Row(
            Button(id='45', text=Const("45"), on_click=on_period_selected),
            Button(id='60', text=Const("60"), on_click=on_period_selected),
            Button(id='90', text=Const("90"), on_click=on_period_selected),
        ),
        Back(Const('назад')),

        getter=getter_period,
        state=MainDialogSG.get_period,

    ),
    Window(
        # Format(),
        Format(as_key_value("🚩 Дата поездки", "{selected_date}").as_html()),
        Format(as_key_value("🚩 Продажа за", "{selected_period} суток").as_html()),
        Format(as_key_value("🚩 Открытие продажи", "{date_of_purchase}\n").as_html()),
        Const(when=F['show_buttons'], text=Italic("〰️ Хотите чтобы я напомнил о покупке билета?").as_html()),

        Row(
            SwitchTo(Const('да'), when=F['show_buttons'], id='get_text_or_voice', state=MainDialogSG.get_text_or_voice),
            Start(Const('новая дата'), id='new_dialog', state=MainDialogSG.start, mode=StartMode.RESET_STACK),
        ),
        Back(Const('назад')),

        getter=getter_date_of_purchase,
        state=MainDialogSG.get_date_of_purchase
    ),
    Window(
        Const(Italic('✏️🎤 Введите текст напоминания или отправьте голосовое сообщение').as_html()),
        MessageInput(
            text_handler,
            content_types=[ContentType.TEXT, ContentType.VOICE]
        ),
        Back(Const('назад')),
        state=MainDialogSG.get_text_or_voice
    ),
    Window(
        Format(as_key_value("🚩 Дата поездки", "{selected_date}").as_html()),
        Format(as_key_value("🚩 Продажа за", "{selected_period} суток").as_html()),
        Format(as_key_value("🚩 Открытие продажи", "{date_of_purchase}").as_html()),
        Format(as_key_value("🚩 Текст напоминания", "{text}\n").as_html()),
        Const(Italic("〰️ Хотите получить напоминание за сутки до открытия продажи?").as_html()),

        Row(
            Button(id='yes', text=Const("да"), on_click=remind_me_selected),
            Button(id='no', text=Const("нет"), on_click=remind_me_selected),
        ),
        Back(Const('назад')),

        getter=getter_remind_me,
        state=MainDialogSG.remind_me
    ),
    Window(
        Const('✔️ Напоминание о покупке билета запланировано\n'),
        Const('⁉️ Чтобы начать сначала, нажмите  меню -> /start'),
        state=MainDialogSG.finish

    )
)
