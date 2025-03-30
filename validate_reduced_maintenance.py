from flight_optimizer import *
import pickle
import os

SOLUTION_DIR = "./benchmarks/reduced_flow_maintenance"

for solution_name in os.listdir(SOLUTION_DIR):
    print(f"testing solution {solution_name}.", end='')
    solution_path = os.path.join(SOLUTION_DIR, solution_name,'solution.pickle')

    solution = pickle.load(open(solution_path, 'rb'))

    valid, reason = solution.is_valide()
    if not valid:
        print(f' found problem: {reason}')
    else:
        print(f" Solution is correct")