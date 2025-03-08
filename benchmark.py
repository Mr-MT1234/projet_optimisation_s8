import pickle
import os
import argparse
from datetime import datetime

import matplotlib.pyplot as plt

from flight_optimizer import *


def problem_path(d: float, p: int, h: int, test_index: int):
    return f"./data/d={d}/p={p}/h={h}/DataCplex_density={d}_p={p}_h={h}_test_{test_index}.dat"


def solution_path(d: float, p: int, h: int, test_index: int):
    return f"./data/d={d}/p={p}/h={h}/Optimal_Solution_density={d}_p={p}_h={h}_test_{test_index}.txt"


D = [0.5, 0.7, 1.0]
P = [10, 20, 30, 40]
H = [7, 15, 21, 30]

parser = argparse.ArgumentParser(
    prog="benchmark",
    description="Solves the flight planing problem provided by the arguments and outputs the results",
)

parser.add_argument(
    "-d",
    "--density",
    type=float,
    choices=D,
    help="The density of the instance",
    required=True,
)
parser.add_argument(
    "-p", "--planes", type=int, choices=P, help="The number of airplanes", required=True
)
parser.add_argument(
    "-hz", "--horizon", type=int, choices=H, help="The horizon", required=True
)
parser.add_argument(
    "-i",
    "--index",
    type=int,
    choices=range(10),
    help="The index of the test problem",
    required=True,
)
parser.add_argument(
    "-m",
    "--method",
    type=str,
    choices=["interval", "flow"],
    help="the mothod to be used",
)

reporter = Reporter()

args = parser.parse_args()

if args.density == 1.0:
    args.density = 1

if args.method == "interval":
    solver = IntervalSolver()
if args.method == "flow":
    solver = FlowSolver()

print("Loading problem ...")
problem = FlightProblem.from_file(
    problem_path(args.density, args.planes, args.horizon, args.index)
)

# for flight in problem.flights:
#     flight.arrival_time += 30

correct_solution = FlightSolution.from_file(
    solution_path(args.density, args.planes, args.horizon, args.index), problem
)

print("Solving ...")

start = datetime.now()
solution = solver.solve(problem)
end = datetime.now()

execution_time = (end - start).total_seconds()

print("Writing solution ...")
fig = reporter.plot_solution(
    [solution, correct_solution], legend=["Found solution", "Optimal solution"]
)

benchmark_dir = f"./benchmarks/{args.method}"
output_dir = os.path.join(
    benchmark_dir,
    f"problem_d={args.density}_p={args.planes}_h={args.horizon}_i={args.index}",
)

if not os.path.exists(benchmark_dir):
    os.makedirs(benchmark_dir)

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

fig.savefig(os.path.join(output_dir, "visualisation.pdf"), format="pdf")

with open("solution.pickle", "wb") as file:
    pickle.dump(solution, file)

reporter.report_txt(
    solution,
    os.path.join(output_dir, "report_found_solution.txt"),
    execution_time=execution_time,
)
reporter.report_txt(
    correct_solution, os.path.join(output_dir, "report_optimal_solution.txt")
)

print("cost delta: ", correct_solution.cost - solution.cost)
print(
    f"cost relative delta: {np.round((correct_solution.cost - solution.cost)/ correct_solution.cost * 100, 3)}%"
)
print("execution time: ", execution_time)