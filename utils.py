from datetime import datetime, timedelta

def get_today_date():
    return datetime.today().strftime('%Y-%m-%d')

def get_date_range(period: str, option: str = "current", custom_value: str = None) -> tuple[str, str]:
    """
    Devuelve un rango de fechas según el periodo ('day', 'week', 'month', 'year') y una opción:
    - 'current': hoy, esta semana, este mes, este año
    - 'last': ayer, semana pasada, mes pasado, año pasado
    - 'custom': se debe especificar custom_value como YYYY-MM-DD (día), YYYY-MM (mes), o YYYY (año)
    """
    today = datetime.today()

    if period == "day":
        if option == "current":
            start = end = today
        elif option == "last":
            start = end = today - timedelta(days=1)
        elif option == "custom":
            try:
                start = end = datetime.strptime(custom_value, "%Y-%m-%d")
            except:
                raise ValueError("Invalid custom_value format for day. Use YYYY-MM-DD")
        else:
            raise ValueError("Invalid option for day")

    elif period == "week":
        if option == "current":
            start = today - timedelta(days=today.weekday())
            end = start + timedelta(days=6)
        elif option == "last":
            start = today - timedelta(days=today.weekday() + 7)
            end = start + timedelta(days=6)
        elif option == "custom":
            try:
                ref_date = datetime.strptime(custom_value, "%Y-%m-%d")
                start = ref_date - timedelta(days=ref_date.weekday())
                end = start + timedelta(days=6)
            except:
                raise ValueError("Invalid custom_value format for week. Use YYYY-MM-DD")
        else:
            raise ValueError("Invalid option for week")

    elif period == "month":
        if option == "current":
            start = today.replace(day=1)
            end = (start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        elif option == "last":
            first_day_current = today.replace(day=1)
            end = first_day_current - timedelta(days=1)
            start = end.replace(day=1)
        elif option == "custom":
            try:
                ref_date = datetime.strptime(custom_value, "%Y-%m")
                start = ref_date.replace(day=1)
                end = (start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            except:
                raise ValueError("Invalid custom_value format for month. Use YYYY-MM")
        else:
            raise ValueError("Invalid option for month")

    elif period == "year":
        if option == "current":
            start = today.replace(month=1, day=1)
            end = today.replace(month=12, day=31)
        elif option == "last":
            start = today.replace(year=today.year - 1, month=1, day=1)
            end = today.replace(year=today.year - 1, month=12, day=31)
        elif option == "custom":
            try:
                ref_year = int(custom_value)
                start = datetime(ref_year, 1, 1)
                end = datetime(ref_year, 12, 31)
            except:
                raise ValueError("Invalid custom_value format for year. Use YYYY")
        else:
            raise ValueError("Invalid option for year")

    else:
        raise ValueError("Invalid period")

    return start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d')
