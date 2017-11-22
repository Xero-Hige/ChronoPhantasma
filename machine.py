import multiprocessing
from time import sleep


class Machine(multiprocessing.Process):
    def __init__(self, machine_queue, job_time):
        multiprocessing.Process.__init__(self)
        self.exit = multiprocessing.Event()

        self.machine_queue = machine_queue
        self.job_time = job_time

    def do_job(self, job_size):
        sleep(self.job_time * job_size)

    def do_process(self):
        job = self.machine_queue.get()
        while job:
            queue, job_size = job
            self.do_job(job_size)
            queue.put(0)
            job = self.machine_queue.get()

    def shutdown(self):
        self.exit.set()
