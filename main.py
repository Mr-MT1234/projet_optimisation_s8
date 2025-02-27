from flight_optimizer.parsing import parse_problem
from flight_optimizer.solvers.interval_solver import IntervalSolver
from flight_optimizer.reporter import Reporter
from flight_optimizer.commun import *

import pickle
import os

import matplotlib.pyplot as plt

problem = parse_problem("./data/d=0.5/p=10/h=7/DataCplex_density=0.5_p=10_h=7_test_0.dat")
if not os.path.exists('test_solution.pickle'):

    solver = IntervalSolver()

    solution = solver.solve(problem)

    with open('test_solution.pickle', 'wb') as f:
        pickle.dump(solution, f)

# with open('test_solution.pickle', 'rb') as f:
#     solution = pickle.load(f)

solution = FlightSolution.load_from_txt('./data/d=0.5/p=10/h=7/Optimal_Solution_density=0.5_p=10_h=7_test_0.txt', problem)

reporter = Reporter()

fig = reporter.plot_solution(solution)
plt.figure(fig)

plt.show()