import logging
import queue
import threading
from typing import Callable, Optional

from .__types import TaskMasterRetentionPolicy, TaskQueueItem
from .__executor import Executor

class TaskQueue:
    def __init__(
        self,
        get_executor: Callable[[], Executor],
        retention_policy: TaskMasterRetentionPolicy = "Memory",
        retention_dir: Optional[str] = None,
    ):

        self.retention_policy = retention_policy
        self.retention_dir = retention_dir
        self.get_executor = get_executor
        self.finished : list[TaskQueueItem] = []
        self.running : list[TaskQueueItem] = []
        self.waiting : Optional[TaskQueueItem] = None
        self.__queue = queue.Queue()
        self.__dequeue_thread = threading.Thread(target=self.dequeue_worker, daemon=True)
        self.__dequeue_thread_running = True
        self.__dequeue_thread.start()

    def enqueue(self, callback: Callable, name : str, *args, **kwargs):
        self.__queue.put(TaskQueueItem(callback=callback, name=name, args=args, kwargs=kwargs))

    def dequeue_worker(self):
        def on_start(t : TaskQueueItem):
            self.running.append(t)
        def on_complete(t : TaskQueueItem):
            self.running.remove(t)
            self.finished.append(t)
        while self.__dequeue_thread_running:
            tqi: TaskQueueItem = self.__queue.get()
            self.waiting = tqi
            exec = self.get_executor()
            self.waiting = None
            self.running.append(tqi)
            exec.execute(
                tqi=tqi,
                onstart=on_start,
                oncomplete=on_complete
            )
    
    def get_finished_items(self):
        q : TaskQueueItem
        for q in self.finished:
            yield q
    
    def get_running_items(self):
        q : TaskQueueItem
        for q in self.running:
            yield q
    
    def get_queue_items(self):
        q : TaskQueueItem
        if self.waiting is not None:
            yield self.waiting
        for q in list(self.__queue.queue):
            yield q
    
    def __del__(self):
        self.__dequeue_thread_running = False
        self.__dequeue_thread.join()
