# EasySchedule

## Get Started
```bash
pip install easyschedule
```

```python
import asyncio
from easyschedule.scheduler import EasyScheduler

scheduler = EasyScheduler()

default_args = {'args': [1, 2, 3]}
every_minute = '* * * * *'
every_5_minutes_wk_end = '*/5, * * * FRI,SAT'

@scheduler(schedule=every_minute, default_args=default_args)
def print_stuff(a, b, c):
    print(f"a {a} b: {b} c {c}")

def print_more_stuff():
    print_stuff(3,4,5)

async def main():
    # start scheduler in background
    sched = asyncio.create_task(scheduler.start())
    await asyncio.sleep(10)

    # add task after scheduler has already started
    scheduler.schedule(print_more_stuff, schedule=cron2)

    await sched

asyncio.run(main())
```
```bash
03-09 10:35:32 EasyScheduler WARNING  weekday_stuff next_run_time: 2021-03-09 10:36:00.843493
03-09 10:35:42 EasyScheduler WARNING  weekend_stuff next_run_time: 2021-03-13 00:31:00.853770
```
## Cron syntax Compatability
#
EasySchedule is capable of parsing most cron schedule syntax

#
## Monthly
First of month at 11:00 PM
```bash
0 23 1 * *
```
#

## Daily
Every 2 Hours
```bash
0 */2 * *
```
#

## Weekends Only 
Every Hour Between 5:30 PM  - 5:30 AM ##
```bash
30 17-23,0-5 * * SAT,SUN
```
## Cron Generator
An easy & interactive way to build a cron schedule is available via <em>[crontab.guru](https://crontab.guru/) </em>

### Note: unsupported syntax (currently)
```bash
@(non-standard) 
@hourly
@daily 
@anually
```

#
## Scheduluing Single Tasks
EasySchedule is complete with single task scheduling

### Usage with 'once' decorator
```python
from datetime import datetime, timedelta

next_year = datetime.now() + timedelta(days=365)

@scheduler.once(date=next_year)
async def future_task():
    ## future work
    pass

# current month: 2021-03-13 00:00:00
@scheduler.once(date_string='2021-04-13 00:00:00')
async def run_at_date():
    ## future work
    pass

# current month: 2021-03-13 00:00:00
@scheduler.once(delta=timedelta(days=3))
async def run_after_delta():
    ## future work
    pass

now_args={'kwargs': {'work': "Lots of work"}}

@scheduler.once(now=True, default_args=now_args)
async def run_now(work):
    ## future work
    print(f"starting {work}")
    pass
```
#
## Schedule a task at or near application startup
```python
notify = {
    'kwargs': { 'emails': ['admin@company.org'] }
    }

@scheduler.delayed_start(delay_in_seconds=30, default_args=notify)
async def notify_online(emails: str):
    message = f"server is operational"
    await send_emails(message, emails)
    #something else

async def get_data():
    return await requests.get('http://data-source')

@scheduler.startup()
async def update_database():
    data = await get_data()
    await db.update(data)
    #something else
```
#
## Schedule a task to run at application shutdown
```python
notify = {
    'kwargs': { 'emails': ['admin@company.org'] }
    }

@scheduler.shutdown(default_args=notify)
async def notify_shutdown(emails: str):
    message = f"server is shutting down"
    await send_emails(message, emails)
    #something else?
```