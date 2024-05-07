from datetime import datetime


def pprint(d):
    from json import dump
    import sys

    dump(d, sys.stdout, indent=2)


def calculate_age(birth_date):
    birth_date = datetime.strptime(birth_date, "%Y-%m-%d")

    today = datetime.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    return age
