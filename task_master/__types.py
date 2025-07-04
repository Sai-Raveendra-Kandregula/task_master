import inspect
import json
from typing import Any, Callable, Literal

TaskMasterRetentionPolicy = Literal["Memory", "Filesystem"]

def shift_indentation(encoded_string : str):
    # Split the string into lines
    lines = encoded_string.splitlines()
    
    # Determine the indentation of the first line
    if not lines:
        return encoded_string  # Return as is if the string is empty
    first_line = lines[0]
    first_line_indentation = len(first_line) - len(first_line.lstrip())
    
    # Shift all lines to the left by the first line's indentation
    shifted_lines = []
    for line in lines:
        shifted_lines.append(line[first_line_indentation:] if len(line) >= first_line_indentation else line)
    
    # Join the lines back into a single string
    return "\n".join(shifted_lines)


class TaskQueueItem:
    __last_id : int = 0
    def __init__(
        self,
        name: str,
        callback: Callable,
        args: tuple,
        kwargs: dict[str, Any],
    ):
        self.id = TaskQueueItem.__last_id + 1
        TaskQueueItem.__last_id = self.id
        self.name = name
        self.callback = callback
        self.callback_fn_raw = shift_indentation(inspect.getsource(callback))
        self.args = args
        self.kwargs = kwargs
        self.result : str | None = None
        self.error : str | None = None
        self.run_time : float = 0.0
        self.is_cancelled : bool = False
    
    def cancel(self):
        """ 
        Cancel this queue item. If the item is already running, it does nothing 
        unless you handle `q_item.is_cancelled` in your callback. 
        (q_item is passed to the callback as a kwarg)
        """
        self.is_cancelled = True
    
    def appendResult(self, res):
        if res is None:
            return
        if self.result is None:
            self.result = ""
        else:
            self.result += "\n"
        def is_literal_type(obj):
            literal_types = (int, float, str, bool, bytes, complex)
            return isinstance(obj, literal_types)
        if is_literal_type(res):
            self.result += str(res)
        else:
            try:
                self.result += json.dumps(res)
            except:
                self.result += json.dumps(repr(res))
    
    def setError(self, e : Exception):
        self.error = str(e)
    
    def dict(
        self,
        state : Literal['running', 'finished', 'queued', 'cancelled'] = 'queued'
    ):
        args = []
        kwargs = {}
        for a in self.args:
            try:
                json.dumps(a)
                args.append(a)
            except:
                args.append(repr(a))
        for k, v in self.kwargs.items():
            try:
                json.dumps(v)
                kwargs[k] = v
            except:
                kwargs[k] = repr(v)
        return {
            **self.__dict__,
            "callback" : self.callback.__name__,
            "state" : state if not self.is_cancelled else "cancelled",
            'args' : args,
            'kwargs' : kwargs,
        }