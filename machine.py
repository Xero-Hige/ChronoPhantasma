import multiprocessing
from time import sleep


class Machine(multiprocessing.Process):
    def __init__(self, machine_queue, client_queues, job_time):
        multiprocessing.Process.__init__(self)
        self.exit = multiprocessing.Event()

        self.machine_queue = machine_queue
        self.client_queues = client_queues
        self.job_time = job_time

    def do_job(self, job_size):
        sleep(self.job_time * job_size)

    def run(self):
        job = self.machine_queue.get()
        while job:
            client_number, job_size = job
            self.do_job(job_size)
            self.client_queues[client_number].put(0)
            job = self.machine_queue.get()

    def shutdown(self):
        self.exit.set()
