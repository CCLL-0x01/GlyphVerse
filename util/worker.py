import multiprocessing
import time
from abc import ABC, abstractmethod

class Worker(ABC):
    '''
    an ABC to run code in another process
    '''
    def __init__(self):
        self.progress = multiprocessing.Value('d', 0.0)
        self.process = None

    def run(self):
        if self.process is None:
            self.process = multiprocessing.Process(target=self.worker)
            self.process.start()

    @abstractmethod
    def worker(self):
        pass

    def get_status(self):
        return {
            'status': 'Running' if self.process.is_alive() else 'Complete',
            'progress': self.progress.value
        }

