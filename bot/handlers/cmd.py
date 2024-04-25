from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.formatting import Italic

cmd_router = Router()


@cmd_router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    # await add_user_to_db(message.from_user.id, message.from_user.username, message.from_user.first_name,
    #                      message.from_user.last_name)
    await message.answer(Italic("hello").as_html())