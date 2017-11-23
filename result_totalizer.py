import multiprocessing


class Totalizer(multiprocessing.Process):
    def __init__(self, in_queue, out_queue):
        multiprocessing.Process.__init__(self)
        self.exit = multiprocessing.Event()

        self.in_queue = in_queue
        self.out_queue = out_queue

        self.jobs = {}

    def shutdown(self):
        self.exit.set()

    def run(self):
        job = self.in_queue.get()
        while job:
            client_number, job_numb, job_time = job

            client_jobs = self.jobs.get(client_number, {})
            stored_job_time = client_jobs.get(job_numb, 0)
            client_jobs[job_numb] = max(stored_job_time, job_time)
            self.jobs[client_number] = client_jobs

            job = self.in_queue.get()

        print("No more jobs")
        for client_number in self.jobs:
            print(client_number)
            accumulated = 0
            total_jobs = 0
            for job, job_time in self.jobs[client_number].items():
                accumulated += job_time
                total_jobs += 1

            self.out_queue.put((client_number, accumulated / total_jobs))
