import operator
from typing import Any

from aiogram.types import CallbackQuery
from aiogram.utils.formatting import as_key_value, as_list, Bold
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import Select, Button, Back, ScrollingGroup
from aiogram_dialog.widgets.text import Const, Format, Case
from apscheduler.job import Job
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from bot.state_groups import ListOfRemindersSG
from bot.utils.from_datetime_to_str import date_to_short_str, date_to_str


async def get_reminders(dialog_manager: DialogManager, **kwargs) -> dict[str, Any]:
    user_id = dialog_manager.event.from_user.id
    apscheduler: AsyncIOScheduler = dialog_manager.middleware_data.get('apscheduler')
    result = list()
    all_jobs: list[Job] = apscheduler.get_jobs(jobstore='sqlite')
    jobs: list[Job] = list(filter(lambda j: j.name == str(user_id), all_jobs))

    for job in jobs:
        result.append((
            date_to_short_str(job.kwargs.get('selected_date')),
            job.kwargs.get('text'),
            job.id
        ))

    return {
        "reminders": result,
        "count": str(len(jobs)),
    }


async def get_reminder(dialog_manager: DialogManager, **kwargs) -> dict[str: str]:
    job_id = dialog_manager.dialog_data.get("job_id")
    apscheduler: AsyncIOScheduler = dialog_manager.middleware_data.get("apscheduler")
    job = apscheduler.get_job(job_id)

    remind_info = as_list(
        as_key_value("Дата поездки", f'{date_to_str(job.kwargs.get("selected_date"))}\n'),
        as_key_value("Дата покупки билета",
                     f'{date_to_str(job.kwargs.get("date_of_purchase"))} (за {job.kwargs.get("selected_period")} дней)\n'),
        as_key_value("Текст напоминания", job.kwargs.get("text")),
    )

    return {"remind_info": remind_info.as_html()}


async def on_reminder_selected(callback: CallbackQuery, widget: Any,
                               manager: DialogManager, job_id: str) -> None:
    manager.dialog_data["job_id"] = job_id
    await manager.switch_to(ListOfRemindersSG.show_reminder)


async def on_delete_selected(callback: CallbackQuery, button: Button,
                             dialog_manager: DialogManager) -> None:
    apscheduler: AsyncIOScheduler = dialog_manager.middleware_data.get("apscheduler")
    apscheduler.remove_job(dialog_manager.dialog_data.get("job_id"))
    await callback.answer("напоминание удалено")
    del dialog_manager.dialog_data["job_id"]
    await dialog_manager.switch_to(ListOfRemindersSG.start)


# диалог список напоминаний
list_reminders_dialog = Dialog(
    Window(
        Const(Bold("📄 Список напоминаний:").as_html()),
        Case(
            {
                "0": Const("            🫲   🫱"),
                ...: Format("           всего: {count} 👇")
            },
            selector="count"
        ),
        ScrollingGroup(
            Select(
                Format("{item[0]} -> {item[1]}"),
                id="s_reminders",
                item_id_getter=operator.itemgetter(2),
                items="reminders",
                on_click=on_reminder_selected,
            ),
            id='scroll',
            width=1,
            height=7
        ),
        state=ListOfRemindersSG.start,
        getter=get_reminders,
    ),
    Window(
        Format('{remind_info}'),
        Back(Const("Назад")),
        Button(Const("Удалить"), id='delete_reminder', on_click=on_delete_selected),
        state=ListOfRemindersSG.show_reminder,
        getter=get_reminder,
    ),
)
