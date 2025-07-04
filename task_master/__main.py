from typing import Callable, Optional

# import nest_asyncio

from .__types import TaskMasterRetentionPolicy
from .__executor import Executor
from .__task_queue import TaskQueue

# nest_asyncio.apply()


class TaskMaster:
    def __init__(
        self,
        *,
        retention_policy: TaskMasterRetentionPolicy = "Memory",
        retention_dir: Optional[str] = None,
        num_executors: int = 1,
        dependencies: Optional[dict] = None,
    ):
        self.retention_policy = retention_policy
        if retention_policy == "Filesystem":
            raise Exception(
                "Filesystem Retention not yet supported."
            )
        if retention_policy == "Filesystem" and retention_dir is None:
            raise Exception(
                "Retention Directory is required for 'Filesystem' retention policy but was not provided."
            )

        self.num_executors = num_executors
        self.dependencies = dependencies if dependencies is not None else {}
        self.__taskqueue = TaskQueue(
            get_executor=self.get_executor,
            retention_policy=retention_policy,
            retention_dir=retention_dir,
        )
        self.executors: list[Executor] = []
        for i in range(num_executors):
            self.executors.append(
                Executor(
                    id=i,
                    dependencies=dependencies,
                )
            )

    def get_executor(self):
        _exec: Executor | None = None
        while _exec is None:
            for i in range(self.num_executors):
                if not self.executors[i].running:
                    _exec = self.executors[i]
        return _exec

    def execute(self, callback: Callable, name: Optional[str] = None, *args, **kwargs):
        # Append to task queue here
        if name is None:
            name = callback.__name__
        return self.__taskqueue.enqueue(callback=callback, name=name, *args, **kwargs)
        # self.executors[0].execute(callback, *args, **kwargs)

    def get_pending_items(self):
        return self.__taskqueue.get_pending_items()

    def get_queue_item(self, task_id : int):
        return self.__taskqueue.get_queue_item(task_id)

    def get_all_queue_items(self):
        return self.__taskqueue.get_all_queue_items()

    def get_finished_items(self):
        return self.__taskqueue.get_finished_items()
        # for exec in self.executors:
        #     finished = [*exec.finished]
        #     finished.reverse()
        #     for q in finished:
        #         yield q

    def get_running_items(self):
        return self.__taskqueue.get_running_items()
        # for exec in self.executors:
        #     running = [*exec.running]
        #     running.reverse()
        #     for q in running:
        #         yield q

    def __del__(self):
        del self.__taskqueue
        for i in range(self.num_executors):
            del self.num_executors[i]
