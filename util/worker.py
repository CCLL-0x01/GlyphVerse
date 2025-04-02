import multiprocessing
from multiprocessing import Manager, Queue, Event, Value, Process
import time
from abc import ABC, abstractmethod
from uuid import uuid4
from typing import Dict,Tuple,Any

class EventlessWorker(ABC):
    '''
    an ABC to run code in another process
    remenber to implement `init`, `worker`
    '''
    manager=None
    task_queue:Queue=None
    SLEEP_INTERVAL=1
    completed_tasks=None
    completed_results=None
    progress=None

    current_task=None
    # current_task_lock=None
    @abstractmethod
    def init(self):
        ...
    
    def __init__(self,manager):
        super().__init__()
        self.manager=manager
        self.task_queue=manager.Queue()
        self.completed_tasks=manager.list()
        self.completed_results=manager.dict()
        self.progress=self.manager.Value('d',0.0)
        # self.current_task_lock=manager.Lock()
        self.current_task=manager.list()
        self.current_task.append(None)
        self.reset_progress()
    
    def reset_progress(self,val=0.0):
        self.progress.value=val
    
    def _daemon(self):
        self.init()
        while True:
            if not self.task_queue.empty():
                id,args=self.task_queue.get()
                # with self.current_task_lock:
                self.current_task[0]=id
                result=self.worker(**args)
                self.completed_tasks.append(id)
                self.completed_results[id]=result
                # with self.current_task_lock:
                self.current_task[0]=None


            time.sleep(self.SLEEP_INTERVAL)

    @abstractmethod
    def worker(self,**kwargs):
        ...

    def _alloc_new_id(self):
        return str(uuid4())

    def add_task(self, args:Dict, new_id=None):
        if not new_id:
            new_id=self._alloc_new_id()
        self.task_queue.put((new_id,args))

    def get_status(self, id)->Tuple[bool, bool, Any]:
        '''returns (is_finished, is_running, result)'''
        # with self.current_task_lock:
        if id == self.current_task[0]:
            return False, True, self.progress.value
        if id in self.completed_tasks:
            return True, False, self.completed_results[id]
        else:
            return False, False, None

    def start(self):
        self.subprocess=Process(
            target=self._daemon
        )
        self.subprocess.daemon=True
        self.subprocess.start()

    def quit(self):
        self.subprocess.kill()

    
    
