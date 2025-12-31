import datetime
import calendar


def first_day_of_month() -> datetime.date:
    today: datetime.date = datetime.date.today()
    return today.replace(day=1)


def last_day_of_month() -> datetime.date:
    today: datetime.date = datetime.date.today()
    last_day: int = calendar.monthrange(today.year, today.month)[1]
    return today.replace(day=last_day)
