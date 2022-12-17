import asyncio


class TasksPool:
    __tasks: list

    max_parallel_tasks_cnt: int

    def __init__(self, max_parallel_tasks_cnt: int):
        self.__tasks = []
        self.max_parallel_tasks_cnt = max_parallel_tasks_cnt

    def __handle_exceptions(self, done, pending):
        for task in done:
            if task.exception() is not None:
                raise task.exception()
        for task in pending:
            if task.exception() is not None:
                raise task.exception()

    async def append(self, task):
        self.__tasks.append(task)
        if len(self.__tasks) > self.max_parallel_tasks_cnt:
            done, pending = await asyncio.wait(self.__tasks, return_when=asyncio.FIRST_EXCEPTION)
            self.__handle_exceptions(done, pending)
            self.__tasks = []

    async def done(self):
        if len(self.__tasks) > 0:
            done, pending = await asyncio.wait(self.__tasks, return_when=asyncio.FIRST_EXCEPTION)
            self.__handle_exceptions(done, pending)
