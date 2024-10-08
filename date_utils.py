import datetime

def get_current_holiday():
    now = datetime.datetime.now()
    easter_month, easter_day = calculate_easter(now.year)

    holiday_periods = {
        "Christmas": (datetime.datetime(now.year, 12, 18), datetime.datetime(now.year, 12, 25)),
        "New Year's": (datetime.datetime(now.year, 12, 31), datetime.datetime(now.year, 1, 1)),
        "Easter": (datetime.datetime(now.year, easter_month, easter_day), datetime.datetime(now.year, easter_month, easter_day)),  # Easter Sunday
        "Fourth of July": (datetime.datetime(now.year, 7, 4), datetime.datetime(now.year, 7, 4))
    }

    # Check if the current date falls within any of the holiday periods
    for holiday, (start, end) in holiday_periods.items():
        if start <= now <= end:
            return holiday
    
    return None

def calculate_easter(year):
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return month, day
