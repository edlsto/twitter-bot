def is_within_xmas_period():
    now = datetime.datetime.now()
    return datetime.datetime(now.year, 12, 18) <= now <= datetime.datetime(now.year, 12, 25)
