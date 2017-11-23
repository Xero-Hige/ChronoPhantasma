import json
import multiprocessing
import sys
from time import sleep

import matplotlib.pyplot as plt

from client import Client
from machine import Machine

plt.rcdefaults()

fig, ax = plt.subplots()

with open(sys.argv[1]) as input_file:
    simulation_params = json.loads(input_file.read())

clients = len(simulation_params["clients"])
machines = len(simulation_params["machines_times"])

machines_times = simulation_params["machines_times"]
clients_params = simulation_params["clients"]

simulation_queue = multiprocessing.Queue()

client_queues = []
for _ in range(clients):
    client_queues.append(multiprocessing.Queue())

machines_queues = []
for _ in range(clients):
    machines_queues.append(multiprocessing.Queue())

clients_list = []
for i in range(len(clients_params)):
    clients_list.append(
            Client(i,
                   client_queues[i],
                   machines_queues,
                   clients_params[i]["lambda"],
                   clients_params[i]["allocation"],
                   simulation_queue)
    )

machines_list = []
for i in range(machines):
    machines_list.append(Machine(machines_queues[i], client_queues, machines_times[i]))

for machine in machines_list:
    machine.start()

for client in clients_list:
    client.start()

sleep(30)

for client in clients_list:
    client.shutdown()

results = []
for client in clients_list:
    client.join()
    results.append(simulation_queue.get())

for machine_queue in machines_queues:
    machine_queue.put(None)

results.sort(key=lambda x: x[0])
ax.barh([x[0] for x in results], [x[1] for x in results])
ax.set_yticks([x[0] for x in results])
ax.set_yticklabels(["Client {:02}".format(x[0] + 1) for x in results])

plt.show()
