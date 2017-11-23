import json
import multiprocessing
import sys
from time import sleep

import matplotlib.pyplot as plt

from client import Client
from machine import Machine
from result_totalizer import Totalizer

plt.rcdefaults()

fig, ax = plt.subplots()

with open(sys.argv[1]) as input_file:
    simulation_params = json.loads(input_file.read())

clients = len(simulation_params["clients"])
machines = len(simulation_params["machines_times"])

machines_times = simulation_params["machines_times"]
clients_params = simulation_params["clients"]

simulation_queue = multiprocessing.Queue()
totalizer_queue = multiprocessing.Queue()

machines_queues = []
for _ in range(clients):
    machines_queues.append(multiprocessing.Queue())

clients_list = []
for i in range(len(clients_params)):
    clients_list.append(
            Client(i,
                   machines_queues,
                   clients_params[i]["lambda"],
                   clients_params[i]["allocation"]
                   )
    )

totalizer = Totalizer(totalizer_queue, simulation_queue)
totalizer.start()

machines_list = []
for i in range(machines):
    machines_list.append(Machine(machines_queues[i], totalizer_queue, machines_times[i]))

for machine in machines_list:
    machine.start()

for client in clients_list:
    client.start()

sleep(20)

for client in clients_list:
    client.shutdown()

for client in clients_list:
    client.join()

for machine_queue in machines_queues:
    machine_queue.put(None)

for machine in machines_list:
    machine.join()

results = []
totalizer_queue.put(None)
for client in clients_list:
    results.append(simulation_queue.get())

results.sort(key=lambda x: x[0])
ax.barh([x[0] for x in results], [x[1] for x in results])
ax.set_yticks([x[0] for x in results])
ax.set_yticklabels(["Client {:02}".format(x[0] + 1) for x in results])

plt.show()
