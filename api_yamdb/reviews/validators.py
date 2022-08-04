import datetime as dt


def validate_year(value):
    if value > dt.date.today().year:
        raise ValueError(f'Некорректный год {value}')
