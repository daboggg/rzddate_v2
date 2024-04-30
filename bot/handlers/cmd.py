from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode

from bot.state_groups import MainDialogSG, ListOfRemindersSG

cmd_router = Router()


# отрабатывает по команде /start
@cmd_router.message(CommandStart())
async def cmd_start(message: Message, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(MainDialogSG.start, mode=StartMode.RESET_STACK)


# отрабатывает по команде /list, отображает список напоминаний
@cmd_router.message(Command(commands="list"))
async def list_reminders(_, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(ListOfRemindersSG.start, mode=StartMode.RESET_STACK)


# отрабатывает по команде /help
@cmd_router.message(Command(commands="help"))
async def list_reminders(message: Message) -> None:
    await message.answer('⁉️ Чтобы начать, нажмите  меню -> /start')
