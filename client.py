import multiprocessing
import random
import time


class Client(multiprocessing.Process):
    def __init__(self, client_queue, machines_queues, production_lambda, distributions):
        multiprocessing.Process.__init__(self)
        self.exit = multiprocessing.Event()

        self.client_queue = client_queue
        self.machines_queues = machines_queues
        self.production_lambda = production_lambda
        self.distributions = distributions

        self.acumulated_time = 0
        self.jobs_allocated = 0

    def create_job(self):
        jobs = [(self.client_queue, job_size) for job_size in self.distributions]

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

    def simulate_jobs(self):
        time.sleep(2 * random.expovariate(self.production_lambda))
        while not self.exit.is_set():
            self.create_job()
            time.sleep(2 * random.expovariate(self.production_lambda))

    def get_average_time(self):
        return self.acumulated_time / self.jobs_allocated
