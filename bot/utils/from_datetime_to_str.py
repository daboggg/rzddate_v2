from datetime import date

months = ["", "января", "февраля", "марта", "апреля",
          "мая", "июня", "июля", "августа", "сентября",
          "октября", "ноября", "декабря", ]

day_of_week = ["в понедельник", "во вторник", "в среду", "в четверг",
               "в пятницу", "в субботу", "в воскресенье", ]


def date_to_str(d: date) -> object:

    return f"{d.day} {months[d.month]} {d.year} г. ({day_of_week[d.weekday()]})"


def date_to_short_str(d: date):

    return f"{d.day} {months[d.month]}"