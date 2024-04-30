from aiogram import Router
from aiogram.types import Message


other_router = Router()


@other_router.message()
async def list_reminders(message: Message) -> None:
    await message.answer('⁉️ Чтобы начать, нажмите  меню -> /start')
