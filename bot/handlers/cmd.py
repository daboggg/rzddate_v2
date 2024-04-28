from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.formatting import Italic
from aiogram_dialog import DialogManager, StartMode

from bot.state_groups import MainDialogSG

cmd_router = Router()


# отрабатывает по команде /start
@cmd_router.message(CommandStart())
async def cmd_start(message:Message, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(MainDialogSG.start, mode=StartMode.RESET_STACK)
