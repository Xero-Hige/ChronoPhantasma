from time import sleep


class Machine:
    def __init__(self, machine_queue, client_queues, job_time):
        self.machine_queue = machine_queue
        self.client_queues = client_queues
        self.job_time = job_time

    def do_job(self, job_size):
        sleep(self.job_time * job_size)

    def do_process(self):
        job = self.machine_queue.get()
        while job:
            self.do_job(job)
            job = self.machine_queue.get()
