import pickle
import os
import argparse
from datetime import datetime

import matplotlib.pyplot as plt

from flight_optimizer import *


def problem_path(d: float, p: int, h: int, test_index: int, max_d: int):
    return f"./data/With maintenance constraints/d={max_d}/DataCplex_density={d}_p={p}_h={h}_test_{test_index}.dat"


def solution_path(d: float, p: int, h: int, test_index: int, max_d: int):
    if max_d == 5:
        return f"./data/With maintenance constraints/d={max_d}/Optimal_Solution_density={d}_p={p}_h={h}_test_{test_index}_dmax_{max_d}.txt"
    else:
        return f"./data/With maintenance constraints/d={max_d}/Optimal_Solution_density={d}_p={p}_h={h}_test_{test_index}.txt"


D = [1.0]
P = [10, 20, 30]
H = [15, 21, 30]
D_max = [4,5]

parser = argparse.ArgumentParser(
    prog="benchmark",
    description="Solves the tail assignement problem with maintenance contraints provided by an instance and outputs the results",
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
    "-dm", "--dmax", type=int, choices=D_max, help="The maximum gap between maintenances in days ", required=True
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
    choices=["reduced", "flow"],
    help="the mothod to be used",
)

reporter = Reporter()

args = parser.parse_args()

if args.density == 1.0:
    args.density = 1

if args.method == "reduced":
    solver = ReducedFlowSolver()
if args.method == "flow":
    solver = FlowSolver()

print("Loading problem ...")
try: 
    problem = FlightProblemMaintenance.from_file(
        problem_path(args.density, args.planes, args.horizon, args.index, args.dmax), args.dmax
    )
except FileNotFoundError:
    print("Error, Could not find instance in the database")
    exit(1)


correct_solution = None

try:
    correct_solution = FlightSolutionMaintenance.from_file(
        solution_path(args.density, args.planes, args.horizon, args.index, args.dmax), problem
    )
except FileNotFoundError:
    print("Warning: The selected instance does not have a corresponding solution file")
except:
    print("Warning: Faced error while parsing the solution file. The file may contain some inconsistancy with the problem")

print("Solving ...")

start = datetime.now()
solution = solver.solve_maintenance(problem)
end = datetime.now()

execution_time = (end - start).total_seconds()

print("Writing solution ...")
fig = reporter.plot_solution(
    [solution], legend=["Found solution"]
)

benchmark_dir = f"./benchmarks/{args.method}_maint"
output_dir = os.path.join(
    benchmark_dir,
    f"problem_d={args.density}_p={args.planes}_h={args.horizon}_i={args.index}_dmax={args.dmax}",
)

if not os.path.exists(benchmark_dir):
    os.makedirs(benchmark_dir)

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

fig.savefig(os.path.join(output_dir, "visualisation.pdf"), format="pdf")

with open(os.path.join(output_dir, "solution.pickle"), "wb") as file:
    pickle.dump(solution, file)

reporter.report_txt(
    solution,
    os.path.join(output_dir, "report_found_solution.txt"),
    execution_time=execution_time,
)

if correct_solution:
    reporter.report_txt(
        correct_solution, os.path.join(output_dir, "report_optimal_solution.txt")
    )
    print("cost delta: ", correct_solution.cost - solution.cost)
    print(
        f"cost relative delta: {np.round((correct_solution.cost - solution.cost)/ correct_solution.cost * 100, 3)}%"
    )
else: 
    print("cost: ", solution.cost)

print("execution time: ", execution_time)

fig.show()
plt.show()