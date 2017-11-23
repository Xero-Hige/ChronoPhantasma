import json
import math
import random
import sys

import numpy

POPULATION_SIZE = 1000

PROBABILITIES = [0.25 / 10] * 10 + [0.25 / 90] * 90 + [0.25 / 400] * 400 + [0.25 / 500] * 499
PROBABILITIES.append(1 - sum(PROBABILITIES))


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

    clients_payoffs = []

    for client_j in range(len(clients_allocations)):
        clients_payoffs.append(compute_payoff(client_j,
                                              clients_allocations,
                                              clients_lambdas,
                                              machines_times,
                                              clients_allocations[client_j])
                               )

    sorted_payoffs = sorted(clients_payoffs)

    min_payoff = sorted_payoffs[0]
    max_payoff = sorted_payoffs[-1]

    global_iterations = 0
    while (min_payoff - max_payoff) > 0.02 or max_payoff >= math.inf and global_iterations < 100:
        print("Global iteration {}".format(global_iterations + 1))

        for client_j in range(len(clients_allocations)):

            old_payoff = clients_payoffs[client_j]
            population = []
            base = clients_allocations[client_j]

            population.append((old_payoff, base[:]))

            while len(population) < POPULATION_SIZE:
                new = generate_random_strategy(machines_times)

                payoff = compute_payoff(client_j, clients_allocations, clients_lambdas, machines_times, new)
                population.append((payoff, new))

            random.shuffle(population)  # To mitigate effect of stable sorting
            population.sort(key=lambda x: x[0])
            new_payoff = population[0][0]
            iterations = 0

            while True:
                if abs(old_payoff - new_payoff) < 0.03:
                    print("Match Client_{} ---> {}".format(client_j, old_payoff))
                    if old_payoff != math.inf:
                        break

                if iterations > 100:
                    break

                old_payoff = new_payoff

                new_population = []
                population_size = len(population)
                for i in range(population_size):

                    keep_prob = 1 - i / population_size

                    if random.random() > keep_prob:
                        continue

                    new_population.append(population[i])

                population = [p for p in new_population if sum(p[1]) == 1]

                indexes = list(range(len(population)))
                probabilities = PROBABILITIES[:len(population)]
                regularization = sum(probabilities)
                probabilities = [x / regularization for x in probabilities]

                while len(population) < population_size:
                    base_index = numpy.random.choice(indexes, p=probabilities)
                    base = population[base_index][1]

                    effect_random = random.random()

                    if effect_random < 0.27:
                        new = mutate(base)

                    elif effect_random < 0.93 and len(population) < POPULATION_SIZE - 1:
                        mate_index = numpy.random.choice(indexes, p=probabilities)
                        mate = population[mate_index][1]

                        new_a, new_b = crossing(base, mate)

                        if sum(new_a) == 1:
                            payoff = compute_payoff(client_j, clients_allocations, clients_lambdas, machines_times,
                                                    new_a)
                            population.append((payoff, new_a))

                        if sum(new_b) == 1:
                            payoff = compute_payoff(client_j, clients_allocations, clients_lambdas, machines_times,
                                                    new_b)
                            population.append((payoff, new_b))

                        continue

                    else:
                        new = generate_random_strategy(machines_times)

                    payoff = compute_payoff(client_j, clients_allocations, clients_lambdas, machines_times, new)
                    population.append((payoff, new))

                random.shuffle(population)
                population.sort(key=lambda x: x[0])
                new_payoff = population[0][0]
                iterations += 1

            clients_allocations[client_j] = population[0][1]

        save_state(clients_allocations, clients_lambdas, machines_times)
        global_iterations += 1
        # GA


def save_state(clients_allocations, clients_lambdas, machines_times):
    clients = []
    for i in range(len(clients_lambdas)):
        clients.append({"lambda": clients_lambdas[i], "allocation": clients_allocations[i]})
    structure = {"machines_times": machines_times, "clients": clients}
    with open(sys.argv[2], 'w') as output_file:
        output_file.write(json.dumps(structure))


def crossing(base, mate):
    pivot = random.randrange(0, len(base))
    chromosome_a_1, chromosome_a_2 = base[:pivot], base[pivot:]
    chromosome_b_1, chromosome_b_2 = mate[:pivot], mate[pivot:]
    m_1 = sum(chromosome_a_2)
    m_2 = sum(chromosome_b_2)

    if m_2 != 0:
        x_1 = m_1 / m_2
    else:
        x_1 = 0

    if m_1 != 0:
        x_2 = m_2 / m_1
    else:
        x_2 = 0

    for i in range(len(chromosome_a_2)):
        chromosome_a_2[i] *= x_1
    for i in range(len(chromosome_b_2)):
        chromosome_b_2[i] *= x_2
    new_a = chromosome_a_1 + chromosome_b_2
    new_b = chromosome_b_1 + chromosome_a_2
    return new_a, new_b


def generate_random_strategy(machines_times):
    new = [random.random() for _ in range(len(machines_times))]
    regularization = sum(new)
    for i in range(len(new)):
        new[i] /= regularization
    return new


def mutate(base):
    new = base[:]
    r_number = random.random()
    if r_number < 0.1:
        random.shuffle(new)

    elif r_number < 0.5:
        i = random.randrange(0, len(base))
        j = random.randrange(0, len(base))

        new[i], new[j] = new[j], new[i]

    else:
        i = random.randrange(0, len(base))
        j = random.randrange(0, len(base))

        gamma = random.random()
        mod = new[i] * gamma
        new[i] -= mod
        new[j] += mod
    return new


def compute_payoff(client_j, clients_allocations, clients_lambdas, machines_times, client_allocations):
    if sum(client_allocations) != 1:
        return math.inf

    payoff = 0
    for machine_i in range(len(machines_times)):
        u_ij = calculate_aviable_time(client_j, machine_i, clients_allocations, clients_lambdas, machines_times)

        # print("Machine {} --> {}".format(machine_i, u_ij))
        if u_ij <= 0:
            payoff = math.inf
            break

        base = u_ij - (client_allocations[machine_i] * clients_lambdas[client_j])
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
