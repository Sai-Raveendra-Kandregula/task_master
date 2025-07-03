import asyncio
import threading
import time
from typing import Callable, Optional
from .__types import TaskQueueItem


class Executor:
    def __init__(
        self,
        *,
        id: int,
        dependencies: dict = {},
    ):
        self.id = id
        self.dependencies = dependencies
        self.tqi: Optional[TaskQueueItem] = None
        self.onstart : Optional[Callable[[TaskQueueItem]]] = None
        self.oncomplete : Optional[Callable[[TaskQueueItem]]] = None

        self.finished : list[TaskQueueItem] = []
        self.cancelled : list[TaskQueueItem] = []
        self.running : list[TaskQueueItem] = []
        
        self.__executor_thread = threading.Thread(target=self.executor_thread, daemon=True)
        self.__executor_thread_running = True
        self.__executor_thread.start()
    
    def executor_thread(self):
        while self.__executor_thread_running:
            if self.tqi is None:
                time.sleep(0.1)
                continue
            self.running.append(self.tqi)
            self.onstart(self.tqi)
            start_time = time.time()
            try:
                res = self.tqi.callback(*self.tqi.args, **self.tqi.kwargs, **self.dependencies, q_item=self.tqi)
                self.tqi.appendResult(res=res)
            except Exception as e:
                self.tqi.setError(e)
            end_time = time.time()
            self.tqi.run_time = end_time - start_time
            self.oncomplete(self.tqi)
            self.running.remove(self.tqi)
            if self.tqi.is_cancelled:
                self.cancelled.append(self.tqi)
            else:
                self.finished.append(self.tqi)
                
            
            self.onstart = None
            self.tqi = None
            self.oncomplete = None
            time.sleep(0.01)
            

    def execute(
        self, 
        tqi : TaskQueueItem,
        onstart : Callable, 
        oncomplete : Callable,
    ):
        if asyncio.iscoroutinefunction(tqi.callback):
            raise Exception("Coroutines are not allowed")
        self.tqi = tqi
        self.onstart = onstart
        self.oncomplete = oncomplete
    
    def __del__(self):
        self.__executor_thread_running = False
        self.__executor_thread.join()
