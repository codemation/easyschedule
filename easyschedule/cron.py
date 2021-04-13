import datetime

# days of week are purposely -1 of standard CRON
# integers
DAYS_OF_WEEK = {
    'MON': 0, 'TUE': 1, 'WED': 2,
    'THU': 3, 'FRI': 4, 'SAT': 5,
    'SUN': 6, '7': 6, 7: 6, 0: 6, 
    '0': 6, '1': 0, '2': 1, '3': 2,
    '4': 3, '5': 4, '6': 5
}

MONTHS_OF_YEAR = { 
    'JAN': 1, 'FEB': 2, 'MAR': 3,
    'APR': 4, 'MAY': 5, 'JUN': 6,
    'JUL': 7, 'AUG': 8, 'SEP': 9,
    'OCT': 10,'NOV': 11,'DEC': 12
}
def parse_schedule_items(items: str, max_range: int):
    if not '*' in items:
        if ',' in items:
            items_split = items.split(',')
            items = []
            for i in items_split:
                step = 1
                if '/' in i:
                    i, step = i.split('/')
                if '-' in i:
                    start, end = i.split('-')
                    items = items + [i for i in range(int(start), int(end)+1, int(step))]   
                else:
                    items.append(i)

            items = [int(i) for i in items]
        elif '-' in items:  
            step = 1
            if '/' in items:
                items, step = items.split('/')
            start, end = items.split('-')
            items = [i for i in range(int(start), int(end)+1, int(step))]
        else:
            items = [int(items)]
    else:
        step = 1
        if '/' in items:
            items, step = items.split('/')
        if '-' in items:
            start, end = items.split('-')
            items = [i for i in range(int(start), int(end)+1, int(step))]
        else:
            items = [i for i in range(0, max_range, int(step))]
    return items

def get_schedule_delay(schedule: str) -> tuple:
    """
    receives cron schedule and calculates next run time
    * * * * *
    min hour day month day(week)
    0-59 0-23 1-31 0-12(JAN-DEC) 0-6(SUN-SAT)
    """
    now = datetime.datetime.now()

    minutes, hours, days, months, weekdays = schedule.split(' ')

    delta = datetime.datetime.now()

    if not weekdays == '*':
        if ',' in weekdays:
            weekdays = weekdays.split(',')
            if weekdays[0] in DAYS_OF_WEEK:
                weekdays = [DAYS_OF_WEEK[d] for d in weekdays]

        elif '-' in weekdays:
            weekdays = weekdays.split('-')
            if weekdays[0] in DAYS_OF_WEEK:
                start = DAYS_OF_WEEK[weekdays[0]]
                end = DAYS_OF_WEEK[weekdays[1]]
                weekdays = [i for i in range(start, end+1)]
        else:
            if weekdays in DAYS_OF_WEEK:
                weekdays = DAYS_OF_WEEK[weekdays]
            weekdays = [weekdays]
    else:
        weekdays = [int(v) for _,v in DAYS_OF_WEEK.items()]

    # months

    if not '*' in months:

        if ',' in months:
            months = months.split(',')
            if months[0] in MONTHS_OF_YEAR:
                months = [MONTHS_OF_YEAR[m] for m in months]
        if '-' in months:
            months = months.split('-')
            if months[0] in MONTHS_OF_YEAR:
                start = MONTHS_OF_YEAR[months[0]]
                end = MONTHS_OF_YEAR[months[1]]
                assert start < end, f"months start cannot be less than end"
                months = [i for i in range(int(start), int(end)+1)]
        else:
            if months.upper() in MONTHS_OF_YEAR:
                months = [MONTHS_OF_YEAR[months.upper()]]
            else:
                months = [int(months)]
    else:
        step =1
        if '/' in months:
            months, step = months.split('/')
        if '-' in months:
            months = months.split('-')
            if months[0] in MONTHS_OF_YEAR:
                start = MONTHS_OF_YEAR[months[0]]
                end = MONTHS_OF_YEAR[months[1]]
                assert start < end, f"months start cannot be less than end"
                months = [i for i in range(int(start), int(end)+1)]
            else:
                if '/' in months:
                    months, step = months.split('/')
                start, end = months.split('-')
                months = [i for i in range(int(start), int(end)+1, int(step))]
        else:
            months = [i for i in range(1,13, int(step))]
    
    months = [int(i) for i in months]

    # days
    days = parse_schedule_items(days, 32)
    # Hours
    hours = parse_schedule_items(hours, 24)
    # minutes
    minutes = parse_schedule_items(minutes, 60)

    current = datetime.datetime.now()

    while True:
        if current.month not in months:
            current = current + datetime.timedelta(hours=23-current.hour, minutes=60-current.minute)
            continue
        if not current.weekday() in weekdays:
            current = current + datetime.timedelta(hours=23-current.hour, minutes=60-current.minute)
            continue

        if not current.day in days:
            current = current + datetime.timedelta(hours=23-current.hour, minutes=60-current.minute)
            continue
        if current.hour not in hours:
            current = current + datetime.timedelta(minutes=59-current.minute, seconds=60-current.second)
            continue
    
        if current.minute not in minutes:
            current = current + datetime.timedelta(seconds=60-current.second)
            continue
        else:
            current = current + datetime.timedelta(seconds=60-current.second)
        break
    delta = current - datetime.datetime.now()
    return current, delta.total_seconds()