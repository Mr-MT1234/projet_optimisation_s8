from flight_optimizer.solvers.interval_solver import IntervalSolver
from flight_optimizer.reporter import Reporter
from flight_optimizer.commun import *
from flight_optimizer.flight_problem import FlightProblem
from flight_optimizer.solution import FlightSolution

import pickle
import os

import matplotlib.pyplot as plt

problem = FlightProblem.from_file("./data/d=0.5/p=10/h=7/DataCplex_density=0.5_p=10_h=7_test_0.dat")
if not os.path.exists('test_solution.pickle'):

    solver = IntervalSolver()

    solution = solver.solve(problem)

    with open('test_solution.pickle', 'wb') as f:
        pickle.dump(solution, f)

with open('test_solution.pickle', 'rb') as f:
    solution1 = pickle.load(f)

solution2 = FlightSolution.from_file('./data/d=0.5/p=10/h=7/Optimal_Solution_density=0.5_p=10_h=7_test_0.txt', problem)

reporter = Reporter()

fig = reporter.plot_solution([solution1, solution2])
plt.figure(fig)

plt.show()