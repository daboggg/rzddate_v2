from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.utils.formatting import as_list, Bold
from apscheduler.job import Job
from apscheduler.schedulers.asyncio import AsyncIOScheduler

done_reminder_router = Router()


# отрабатывает при нажатии кнопки '✔️ Понятно'
@done_reminder_router.callback_query(F.data.startswith("done_remind"))
async def done_reminder(callback: CallbackQuery, apscheduler: AsyncIOScheduler) -> None:
    tmp = callback.data.split(":")
    job_id = tmp[1]

    job: Job = apscheduler.get_job(job_id)

    # форматирование текста для напоминания
    format_text = as_list(
        Bold('👍 Выполнено\n'),
        '⁉️ Чтобы начать, нажмите  меню -> /start'
    )

    await callback.answer()
    await callback.message.edit_text(format_text.as_html())
    job.remove()
