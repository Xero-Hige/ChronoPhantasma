import json
import math
import sys


def main():
    with open(sys.argv[1]) as input_file:
        simulation_params = json.loads(input_file.read())

    machines_times = simulation_params["machines_times"]
    clients_params = simulation_params["clients"]

    clients_allocations = []
    clients_lambdas = []

    for i in range(len(clients_params)):
        clients_allocations.append(clients_params[i]["allocation"])
        clients_lambdas.append(clients_params[i]["lambda"])

    # GA
    client_j = 0

    payoff = compute_payoff(client_j, clients_allocations, clients_lambdas, machines_times)

    # print("Payoff {}".format(payoff))

    # GA

    clients = []
    for i in range(len(clients_lambdas)):
        clients.append({"lambda": clients_lambdas[i], "allocation": clients_allocations[i]})

    structure = {"machines_times": machines_times, "clients": clients}

    with open(sys.argv[2], 'w') as output_file:
        output_file.write(json.dumps(structure))


def compute_payoff(client_j, clients_allocations, clients_lambdas, machines_times):
    payoff = 0
    for machine_i in range(len(machines_times)):
        u_ij = calculate_aviable_time(client_j, machine_i, clients_allocations, clients_lambdas, machines_times)

        # print("Machine {} --> {}".format(machine_i, u_ij))
        if u_ij <= 0:
            payoff = -1
            break

        base = u_ij - (clients_allocations[client_j][machine_i] * clients_lambdas[client_j])
        # print("Base {} --> {}".format(machine_i, base))
        if base <= 0:
            payoff = math.inf
            break

        payoff += (u_ij / base ** 2)
        # print(payoff)
    return payoff


def calculate_aviable_time(client_j, machine_i, clients_allocations, clients_lambdas, machines_times):
    sumatory = 0
    u_i = 1 / machines_times[machine_i]  # Jobs per second that can handle
    for client_k in range(len(clients_allocations)):
        if client_k == client_j:
            continue

        sumatory += (clients_allocations[client_k][machine_i] * clients_lambdas[client_k])

    return u_i - sumatory


if __name__ == '__main__':
    main()
