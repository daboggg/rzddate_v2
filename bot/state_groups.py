from aiogram.fsm.state import StatesGroup, State


class MainDialogSG(StatesGroup):
    start = State()
    get_period = State()
    get_date_of_purchase = State()
    get_text_or_voice = State()
    remind_me = State()
    finish = State()
