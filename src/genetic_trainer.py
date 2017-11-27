import json
import math
import random
import sys

MAX_GLOBAL_ITERATIONS = 100

GA_PAYOFFS_DIFFS = 0.005

RANDOM_OFFSPRING_P = 0.10
MUTATED_OFFSPRING_P = RANDOM_OFFSPRING_P + 0.20

BEST_FITS_TOURNAMENT_K = 5

MAX_GA_ITERATIONS = 100

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
    while (min_payoff - max_payoff) > 0.005 or max_payoff >= math.inf and global_iterations < MAX_GLOBAL_ITERATIONS:
        if global_iterations + 1 == MAX_GLOBAL_ITERATIONS:
            print("Last iteration {}".format(global_iterations + 1))

        clients_payoffs = []
        for client_j in range(len(clients_allocations)):
            calculate_client_allocations(client_j, clients_allocations, clients_lambdas, clients_payoffs,
                                         machines_times)

        save_state(clients_allocations, clients_lambdas, machines_times)
        global_iterations += 1
        # GA


def calculate_client_allocations(client_j, clients_allocations, clients_lambdas, clients_payoffs, machines_times):
    old_payoff = compute_payoff(client_j,
                                clients_allocations,
                                clients_lambdas,
                                machines_times,
                                clients_allocations[client_j])
    population = []
    base = clients_allocations[client_j]
    population.append((old_payoff, base[:]))

    while len(population) < POPULATION_SIZE:
        new = generate_random_strategy(machines_times)
        add_to_population(client_j, clients_allocations, clients_lambdas, machines_times, new, population)

    random.shuffle(population)  # To mitigate effect of stable sorting
    population.sort(key=lambda x: x[0])
    new_payoff = population[0][0]
    iterations = 0

    while True:
        if abs(old_payoff - new_payoff) < GA_PAYOFFS_DIFFS:
            if old_payoff != math.inf:  # Just to prevent wrong results
                break

        if iterations > MAX_GA_ITERATIONS:
            break

        old_payoff = new_payoff

        # Chooses new generation survivors based on a 1vs1 tournament selection
        population = tournament_selection(population, 1)

        regenerate_population(client_j, clients_allocations, clients_lambdas, machines_times, population)

        random.shuffle(population)
        population.sort(key=lambda x: x[0])
        new_payoff = population[0][0]
        iterations += 1

    clients_allocations[client_j] = population[0][1]
    clients_payoffs.append(new_payoff)


def regenerate_population(client_j, clients_allocations, clients_lambdas, machines_times, population):
    population_size = len(population)

    best_fits = tournament_selection(population, BEST_FITS_TOURNAMENT_K)
    while len(population) < population_size:
        effect_random = random.random()

        # Creates random offsprings
        if effect_random <= RANDOM_OFFSPRING_P or len(population) == POPULATION_SIZE - 1:
            new = generate_random_strategy(machines_times)
            add_to_population(client_j, clients_allocations, clients_lambdas, machines_times, new, population)
            continue

        base_individual = random.choice(best_fits)

        # Creates mutated offsprings
        if effect_random < MUTATED_OFFSPRING_P:
            new = mutate(base_individual)
            add_to_population(client_j, clients_allocations, clients_lambdas, machines_times, new, population)
            continue

        # Creates crossed offsprings
        mate = random.choice(best_fits)

        offspring_a, offspring_b = crossing(base_individual, mate)
        add_to_population(client_j, clients_allocations, clients_lambdas, machines_times, offspring_a, population)
        add_to_population(client_j, clients_allocations, clients_lambdas, machines_times, offspring_b, population)


def tournament_selection(population, k):
    """Selects a subset of the population based on a k-tournament selection"""
    winners = []

    population = population[:]
    random.shuffle(population)

    while len(population) > k:
        individual_a = population.pop()
        individual_b = population.pop()

        survivor = individual_a if individual_a[0] < individual_b[0] else individual_b

        winners.append(survivor)

    for individual in population:
        winners.append(individual)

    return winners


def add_to_population(client_j, clients_allocations, clients_lambdas, machines_times, new_strategy, population):
    """Adds a new allocation strategy to the population list"""
    if sum(new_strategy) != 1:
        return
    payoff = compute_payoff(client_j, clients_allocations, clients_lambdas, machines_times, new_strategy)
    population.append((payoff, new_strategy))


def save_state(clients_allocations, clients_lambdas, machines_times):
    """Stores the actual state of the algorithm in a way that can be used by the simulator"""
    clients = []
    for i in range(len(clients_lambdas)):
        clients.append({"lambda": clients_lambdas[i], "allocation": clients_allocations[i]})
    structure = {"machines_times": machines_times, "clients": clients}
    with open(sys.argv[2], 'w') as output_file:
        output_file.write(json.dumps(structure))


def crossing(base, mate):
    """Generates 2 offsprings swapping chromosomes"""
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


def mutate(base_strategy):
    """Mutates an individual reallocating chromosomes"""
    new_strategy = base_strategy[:]
    r_number = random.random()

    # Random full permutations
    if r_number < 0.1:
        random.shuffle(new_strategy)
        return new_strategy

    i = random.randrange(0, len(base_strategy))
    j = random.randrange(0, len(base_strategy))

    # Random single swap
    if r_number < 0.7:
        new_strategy[i], new_strategy[j] = new_strategy[j], new_strategy[i]

    # Random reallocation
    else:
        gamma = random.random()
        mod = new_strategy[i] * gamma
        new_strategy[i] -= mod
        new_strategy[j] += mod

    return new_strategy


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
