# Task Master

A Brokerless Task Queue Executor, written in pure python.

## Usage

```py
from task_master import TaskMaster
import logging

logger = logging.getLogger(__name__)

tsk_mstr = TaskMaster(
    dependencies={
        "logger" : logger
    }
)

def init_msg(logger : logging.Logger, *args, **kwargs):
    logger.info(f"[task_master] Initialized")
tsk_mstr.execute(init_msg)
```

## Limitations

- The Callback can only be synchronous. Behaviour for async callbacks is untested and hence unknown.
- Filesystem retention of the task queues is not yet supported.