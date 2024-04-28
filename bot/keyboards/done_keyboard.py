from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def done_kb(job_id: str) -> InlineKeyboardMarkup:
    ikb = InlineKeyboardBuilder()

    ikb.button(text=f'✔️ Понятно', callback_data=f'done_remind:{job_id}')

    return ikb.adjust().as_markup()