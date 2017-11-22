import multiprocessing
import random
import time


class Client(multiprocessing.Process):
    def __init__(self, client_number, client_queue, machines_queues, production_lambda, distributions, out_queue):
        multiprocessing.Process.__init__(self)
        self.exit = multiprocessing.Event()

        self.client_number = client_number
        self.client_queue = client_queue
        self.machines_queues = machines_queues
        self.production_lambda = production_lambda
        self.distributions = distributions

        self.acumulated_time = 0
        self.jobs_allocated = 0
        self.out_queue = out_queue

    def create_job(self):
        jobs = [(self.client_number, job_size) for job_size in self.distributions]

        start_time = time.time()
        for i in range(len(jobs)):
            if jobs[i][1] == 0:
                continue
            self.machines_queues[i].put(jobs[i])

        for i in range(len(jobs)):
            if jobs[i][1] == 0:
                continue
            self.client_queue.get()
        total_time = time.time() - start_time

        self.acumulated_time += total_time
        self.jobs_allocated += 1

    def shutdown(self):
        self.exit.set()

    def run(self):
        time.sleep(2 * random.expovariate(self.production_lambda))
        while not self.exit.is_set():
            self.create_job()
            time.sleep(2 * random.expovariate(self.production_lambda))
        self.out_queue.put((self.client_number, self.get_average_time()))

    def get_average_time(self):
        return self.acumulated_time / self.jobs_allocated
