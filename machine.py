import multiprocessing
from time import sleep, time


class Machine(multiprocessing.Process):
    def __init__(self, machine_queue, totalizer_queue, job_time):
        multiprocessing.Process.__init__(self)
        self.exit = multiprocessing.Event()

        self.machine_queue = machine_queue
        self.totalizer_queue = totalizer_queue
        self.job_time = job_time

    def do_job(self, job_size):
        sleep(self.job_time * job_size)

    def run(self):
        job = self.machine_queue.get()
        while job:
            client_number, job_numb, job_size, start_time = job
            self.do_job(job_size)
            end_time = time()
            self.totalizer_queue.put((client_number, job_numb, end_time - start_time))
            job = self.machine_queue.get()
        print("Machine ended")

    def shutdown(self):
        self.exit.set()
