import asyncio
from easyschedule import EasyScheduler

scheduler = EasyScheduler()

default_args = {'args': [1, 2, 3]}
weekday_every_minute = '* * * * MON-FRI'

@scheduler(schedule=weekday_every_minute, default_args={'kwargs': {'url': 'test'}})
def minute_stuff(url):
    print(f"minute_stuff: url - {url}")

@scheduler(schedule=weekday_every_minute, default_args=default_args)
def weekday_stuff(a, b, c):
    print(f"a {a} b: {b} c {c}")

@scheduler.delayed_start(delay_in_seconds=30)
async def delay_startup():
    print(f"## startup task - started ##")
    await asyncio.sleep(10)
    print(f"## startup task - ended ##")

@scheduler.shutdown()
async def shutdown():
    print(f"## shutdown task - started ##")
    await asyncio.sleep(10)
    print(f"## shutdown task - ended ##")

@scheduler.once(date_string='2022-03-12 16:18:03')
async def next_year():
    print(f"That was a long year")

async def main():
    # start scheduler
    sched = asyncio.create_task(scheduler.start())
    await asyncio.sleep(10)

    # dynamicly schedule task
    wk_end_args = {'kwargs': {'count': 5}}
    weekend = '30 17-23,0-5 * * SAT,SUN'

    def weekend_stuff(count: int):
        for _ in range(count):
            print_stuff(3,4,5)
            print_stuff(5,6,7)

    scheduler.schedule(
        weekend_stuff, 
        schedule=weekend,
        default_args=wk_end_args
    )
    await sched

asyncio.run(main())