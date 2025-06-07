from datetime import datetime, timedelta

def get_today_date():
    return datetime.today().strftime('%Y-%m-%d')

def get_date_range(period, option, custom_value=None):
    today = datetime.today()

    if period == "day":
        if option == "current":
            start = end = today
        elif option == "last":
            start = end = today - timedelta(days=1)
        elif option == "custom":
            start = end = datetime.strptime(custom_value, "%Y-%m-%d")

    elif period == "week":
        if option == "current":
            start = today - timedelta(days=today.weekday())
            end = start + timedelta(days=6)
        elif option == "last":
            end = today - timedelta(days=today.weekday() + 1)
            start = end - timedelta(days=6)
        elif option == "custom":
            start = datetime.strptime(custom_value, "%Y-%m-%d")
            end = start + timedelta(days=6)

    elif period == "month":
        if option == "current":
            start = today.replace(day=1)
        elif option == "last":
            first_day_this_month = today.replace(day=1)
            end = first_day_this_month - timedelta(days=1)
            start = end.replace(day=1)
            return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")
        elif option == "custom":
            start = datetime.strptime(custom_value, "%Y-%m")
        end = (start.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)

    elif period == "year":
        if option == "current":
            start = today.replace(month=1, day=1)
            end = today.replace(month=12, day=31)
        elif option == "last":
            year = today.year - 1
            start = datetime(year, 1, 1)
            end = datetime(year, 12, 31)
        elif option == "custom":
            year = int(custom_value)
            start = datetime(year, 1, 1)
            end = datetime(year, 12, 31)

    return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")