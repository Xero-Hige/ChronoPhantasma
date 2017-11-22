import multiprocessing
import random
from time import sleep

from client import Client
from machine import Machine

clients = 20
machines = 4

times = [0.1, 0.2, 0.3, 1]
allocations = [1, 0, 0, 0]
lambdas = [0.5] * 20

simulation_queue = multiprocessing.Queue()

client_queues = []
for _ in range(clients):
    client_queues.append(multiprocessing.Queue())

machines_queues = []
for _ in range(clients):
    machines_queues.append(multiprocessing.Queue())

clients_list = []
for i in range(clients):
    random.shuffle(allocations)
    clients_list.append(
            Client(i,
                   client_queues[i],
                   machines_queues,
                   lambdas[i],
                   tuple(allocations))
    )

machines_list = []
for i in range(machines):
    machines_list.append(Machine(machines_queues[i], client_queues, times[i]))

for machine in machines_list:
    machine.start()

for client in clients_list:
    client.start()

sleep(30)

for client in clients_list:
    client.shutdown()

for client in clients_list:
    client.join()

for machine_queue in machines_queues:
    machine_queue.put(None)
