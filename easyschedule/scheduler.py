import asyncio
import logging
from datetime import datetime, timedelta
from typing import Callable, Optional
from easyschedule.cron import get_schedule_delay

class EasyScheduler:
    def __init__(
        self,
        logger: Optional[logging.Logger] = None,
        debug: Optional[bool] = False
    ):
        self.scheduled_tasks = {}
        self.single_tasks = []
        self.loop = None
        ## logging
        level = 'DEBUG' if debug else None
        self.setup_logger(logger=logger, level=level)
    
    def setup_logger(
        self, 
        logger: logging.Logger = None, 
        level: str = None
    ) -> None:
        if logger == None:
            level = logging.DEBUG if level == 'DEBUG' else logging.WARNING
            logging.basicConfig(
                level=level,
                format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                datefmt='%m-%d %H:%M:%S'
            )
            self.log = logging.getLogger(f'EasyScheduler')
            self.log.propogate = False
        else:
            self.log = logger
    def __call__(
        self,
        schedule: str,
        default_args: dict = {'args': [], 'kwargs': {}}
    ) -> Callable:
        if not 'args' in default_args:
            default_args['args'] = []
        if not 'kwargs' in default_args: 
            default_args['kwargs'] = {}
        def scheduler(func):
            async def scheduled(*args, **kwargs):
                result = func(*args, **kwargs)
                if asyncio.iscoroutine(result):
                    result = await result
                return result
            scheduled.__name__ = func.__name__
            self.scheduled_tasks[scheduled.__name__] = {
                'func': scheduled,
                'schedule': schedule,
                'default_args': default_args
            }
            if self.loop:
                self.schedule_task(scheduled.__name__)
            return func
        return scheduler
    def schedule(
        self, 
        task: Callable, 
        schedule: str,
        default_args: dict = {}
    ):
        """
        schedule a recurring task 
        """
        self(schedule=schedule, default_args=default_args)(task)
    def run_once(
        self,
        func: Callable,
        date: Optional[datetime] = None,
        date_string: Optional[str] = None,
        delta: Optional[timedelta] = None,
        now: Optional[bool] = False,
        on_event: Optional[str] = None,
        default_args: Optional[dict] = None,
    ):
        time_now = datetime.now()
        delay = None
        if date and date >= time_now:
            delay = date - time_now
        if date_string:
            date = datetime.fromisoformat(date_string)
            if date >= time_now:
                delay = date - time_now
        if delta:
            if not isinstance(delta, timedelta):
                raise Exception(f"delta is type {type(delta)}, expected {timedelta}")
            delay = delta.total_seconds()
        if now:
            delay = datetime.now() - time_now
        if isinstance(delay, timedelta):
            delay = delay.total_seconds()

        if not default_args:
            default_args = {}
        if not 'args' in default_args:
            default_args['args'] = []
        if not 'kwargs' in default_args:
            default_args['kwargs'] = {}

        if on_event and on_event == 'shutdown':
            async def shutdown_task():
                try:
                    while True:
                        await asyncio.sleep(60)
                except asyncio.CancelledError:
                    time_now = datetime.now()
                    self.log.warning(f"shutdown task {func.__name__} triggered at {time_now}")
                    try:
                        await func(*default_args['args'], **default_args['kwargs'])
                    except Exception as e:
                        self.log.exception(f"error running shutdown task - {task}")
                        return

            if self.loop:
                asyncio.create_task(shutdown_task())
            else:
                self.single_tasks.append(shutdown_task)
            return
        
        async def single_task():
            try:
                run_time = time_now + timedelta(seconds=delay)
                self.log.warning(f"single task {func.__name__} scheduled to run at {run_time} in {delay} s")
                await asyncio.sleep(delay)
                try:
                    await func(*default_args['args'], **default_args['kwargs'])
                except Exception as e:
                    if isinstance(e, asyncio.CancelledError):
                        raise e
                    self.log.exception(f"error running single task - {func.__name__}")
            except asyncio.CancelledError:
                return
        
        if self.loop:
            asyncio.create_task(single_task())
        else:
            self.single_tasks.append(single_task)
        return
    def once(
        self,
        date: Optional[datetime] = None,
        date_string: Optional[str] = None,
        delta: Optional[timedelta] = None,
        now: Optional[bool] = False,
        default_args: Optional[dict] = None
    ):
        """
        Decoractor
            runs a single task at at input date, date_string, delta, now        
        """
        def once_decorator(func):
            self.run_once(
                func,
                date=date,
                date_string=date_string,
                delta=delta,
                now=now,
                default_args=default_args
            )
            return func
        return once_decorator
    def startup(
        self,
        default_args: Optional[dict] = None
    ) -> Callable:
        """
        decorator
            runs a single task right after scheduler.start()
        Optional:
            default_args = {'args': [], 'kwargs': {}}
        """
        if self.loop and self.loop.is_running():
            raise Exception(f"scheduler has already started - cannot add startup tasks")
        def startup_decor(func):

            self.run_once(
                func,
                now=True,
                default_args=default_args
            )
            return func
        return startup_decor        
    def delayed_start(
        self,
        delay_in_seconds: int = 60,
        default_args: Optional[dict] = None
    ):  
        """
        decorator
            runs a single task after scheduler.start() with a delay
        
        delay_in_seconds: int = 60 #Default
        Optional:
            default_args = {'args': [], 'kwargs': {}}
        """
        def delayed_start_decor(func):
            self.run_once(
                func,
                delta=timedelta(seconds=delay_in_seconds),
                default_args=default_args
            )
            return func
        return delayed_start_decor
    def shutdown(
        self,
        default_args: Optional[dict] = None
    ):
        """
        decorator
            runs a single task after shutdown is detected
        
        Optional:
            default_args = {'args': [], 'kwargs': {}}
        """
        def shutdown_decor(func):
            self.run_once(
                func,
                default_args=default_args,
                on_event='shutdown'
            )
            return func
        return shutdown_decor
    
            
    def schedule_task(self, task: str) -> None:
        async def scheduled_task():
            try:
                while True:
                    func = self.scheduled_tasks[task]['func']
                    schedule = self.scheduled_tasks[task]['schedule']
                    default_args = self.scheduled_tasks[task]['default_args']
                    next_run_time, delay = get_schedule_delay(schedule)
                    self.log.warning(f"{task} next_run_time: {next_run_time} - default_args: {default_args}")
                    await asyncio.sleep(delay)
                    try:
                        await func(*default_args['args'], **default_args['kwargs'])
                    except Exception as e:
                        self.log.exception(f"error running scheduled task - {task}")
            except asyncio.CancelledError:
                return
        self.log.debug(f"schedule_task called for {self.scheduled_tasks[task]}")
        self.scheduled_tasks[task]['task'] = self.loop.create_task(
            scheduled_task()
        )
    async def start(self):
        if not self.loop:
            self.loop = asyncio.get_running_loop()
        for task in self.scheduled_tasks:
            self.schedule_task(task)
        for task in self.single_tasks:
            asyncio.create_task(task())
        try:
            while True:
                await asyncio.sleep(60)
        except asyncio.CancelledError:
            return