import multiprocessing
import random
import time


class Client(multiprocessing.Process):
    def __init__(self, client_number, machines_queues, production_lambda, distributions):
        multiprocessing.Process.__init__(self)
        self.exit = multiprocessing.Event()

        self.client_number = client_number
        self.machines_queues = machines_queues
        self.production_lambda = production_lambda
        self.distributions = distributions

        self.accumulated_time = 0
        self.jobs_allocated = 0

    def create_job(self, job_number):
        jobs = [(self.client_number, job_number, job_size) for job_size in self.distributions]

        for i in range(len(jobs)):
            if jobs[i][-1] == 0:
                continue
            self.machines_queues[i].put(jobs[i] + (time.time(),))

    def shutdown(self):
        self.exit.set()

    def run(self):
        time.sleep(random.expovariate(self.production_lambda))
        i = 0
        while not self.exit.is_set():
            self.create_job(i)
            time.sleep(random.expovariate(self.production_lambda))
            i += 1
        print(">>Client {} ended<<".format(self.client_number))
