from datetime import date
from typing import Dict

from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Calendar, CalendarScope, CalendarUserConfig
from aiogram_dialog.widgets.kbd.calendar_kbd import CalendarScopeView, CalendarDaysView, CalendarMonthView, \
    CalendarYearsView
from aiogram_dialog.widgets.text import Text, Format
from babel.dates import get_month_names, get_day_names


class Month(Text):
    async def _render_text(self, data, manager: DialogManager) -> str:
        selected_date: date = data["date"]
        locale = manager.event.from_user.language_code
        return get_month_names(
            'wide', context='stand-alone', locale=locale,
        )[selected_date.month].title()


class WeekDay(Text):
    async def _render_text(self, data, manager: DialogManager) -> str:
        selected_date: date = data["date"]
        locale = manager.event.from_user.language_code
        return get_day_names(
            width="short", context='stand-alone', locale=locale,
        )[selected_date.weekday()].title()


class MarkedDay(Text):
    def __init__(self, mark: str, other: Text):
        super().__init__()
        self.mark = mark
        self.other = other

    async def _render_text(self, data, manager: DialogManager) -> str:
        current_date: date = data["date"]
        serial_date = current_date.isoformat()
        selected = manager.dialog_data.get("selected_dates", [])
        if serial_date in selected:
            return self.mark
        return await self.other.render_text(data, manager)


# расширение виджета календаря
class CustomCalendar(Calendar):
    def _init_views(self) -> Dict[CalendarScope, CalendarScopeView]:
        return {
            CalendarScope.DAYS: CalendarDaysView(
                self._item_callback_data, self.config,
                # today_text=Format("***"),
                # date_text=MarkedDay("✓", DATE_TEXT),
                # today_text=MarkedDay("✓", TODAY_TEXT),
                header_text="- " + Month() + " -",
                weekday_text=WeekDay(),
                next_month_text=Month() + " >>",
                prev_month_text="<< " + Month(),
            ),
            CalendarScope.MONTHS: CalendarMonthView(
                self._item_callback_data,
                month_text=Month(),
                header_text="- " + Format("{date:%Y}") + " -",
                this_month_text="[" + Month() + "]",
                config=self.config,
            ),
            CalendarScope.YEARS: CalendarYearsView(
                self._item_callback_data, self.config,
            ),
        }

    async def _get_user_config(
            self,
            data: Dict,
            manager: DialogManager,
    ) -> CalendarUserConfig:
        return CalendarUserConfig(
            firstweekday=7,
        )
