import pickle
import os
from datetime import datetime
import itertools
import csv

import matplotlib.pyplot as plt

from flight_optimizer import *

SOLUTION_TIMEOUT = 30 * 60  # in seconds
BENCHMARK_OUPUT_DIR = "./benchmarks/"


def problem_path(d: float, p: int, h: int, max_d: int, test_index: int):
    return f"./data/With maintenance constraints/d={max_d}/DataCplex_density={d}_p={p}_h={h}_test_{test_index}.dat"


def solution_path(d: float, p: int, h: int, max_d: int, test_index: int):
    if max_d == 5:
        return f"./data/With maintenance constraints/d={max_d}/Optimal_Solution_density={d}_p={p}_h={h}_test_{test_index}_dmax_{max_d}.txt"
    else:
        return f"./data/With maintenance constraints/d={max_d}/Optimal_Solution_density={d}_p={p}_h={h}_test_{test_index}.txt"


D_MAX = [4, 5]
D = [1]
P = [10, 20, 30]
H = [15, 21, 30]


@dataclass
class BenchmarkResult:
    execution_time: float
    cost: float
    gap: float
    relative_gap: float
    valid: bool
    optimal: bool


def benchmark_solver(
    solver: Solver, problem, optimal_solution, name, instance
) -> BenchmarkResult:
    # for flight in problem.flights:
    #     flight.arrival_time += 30

    start_flow = datetime.now()
    solution = solver.solve_maintenance(problem, timeout=SOLUTION_TIMEOUT)
    end_flow = datetime.now()
    solution_time = (end_flow - start_flow).total_seconds()

    # for flight in problem.flights:
    #     flight.arrival_time -= 30
    if solution:
        cost = solution.cost
        gap = cost - optimal_solution.cost

        print("Found optimal solution:")
        print("\t cost:", cost)
        print("\t time:", solution_time)
        print("\t gap:", gap)

        solution_dir = os.path.join(
            BENCHMARK_OUPUT_DIR,
            name,
            "problem_d={}_p={}_h={}_dmax={}_i={}".format(*instance),
        )
        if not os.path.exists(solution_dir):
            os.makedirs(solution_dir)

        solution_file_dir = os.path.join(
            solution_dir,
            "solution.pickle",
        )
        print("saving solution to:", solution_file_dir)
        with open(solution_file_dir, "wb") as f:
            pickle.dump(solution, f)

        reporter = Reporter()
        timeline_file_dir = os.path.join(
            solution_dir,
            "timeline.pdf",
        )
        graph_file_dir = os.path.join(
            solution_dir,
            "graph.pdf",
        )
        print(f"saving figures to: {timeline_file_dir} and {graph_file_dir}")
        timeline = reporter.plot_solution([solution], legend=[f"{name} solution"])
        graph = reporter.plot_solution_graph(solution)
        timeline.savefig(timeline_file_dir)
        graph.savefig(graph_file_dir)

        report_file_dir = os.path.join(
            solution_dir,
            "report.txt",
        )
        print("wrinting report to:", report_file_dir)
        reporter.report_txt(solution, report_file_dir, solution_time)
    else:
        print("Timeout")
        gap = float("nan")
        cost = float("nan")

    relative_gap = round(gap / optimal_solution.cost * 100, 2)

    return BenchmarkResult(
        solution_time,
        cost,
        gap,
        relative_gap,
        solution.is_valide()[0] if solution else False,
        solution_time < SOLUTION_TIMEOUT,
    )


flow_solver = FlowSolver()
reduced_solver = ReducedFlowSolver()

table_dir = os.path.join(BENCHMARK_OUPUT_DIR, "benchmark_maintenance")

if not os.path.exists(table_dir):
    os.makedirs(table_dir)


already_benchmarked = set()
comparaison_file = os.path.join(table_dir, "comparaison.csv")
if os.path.exists(comparaison_file):
    with open(comparaison_file, "r") as f:
        reader = csv.reader(f, delimiter=",")
        next(reader)

        for (density, planes, horizon, d_max, i, *rest) in reader:
            density, planes, horizon, d_max, i = (
                float(density),
                int(planes),
                int(horizon),
                int(d_max),
                int(i),
            )
            if density == 1.0:
                dentity = 1
            already_benchmarked.add((density, planes, horizon, d_max, i))
else:
    with open(comparaison_file, "w") as f:
        f.write(
            "density, planes, horizon, d_max, index, reduced_calc_time (s), reduced_cost, reduced_gap, reduced_relative_gap (%), valid?, optimal?\n"
        )


print(already_benchmarked)

with open(comparaison_file, "a", newline="") as f:
    writer = csv.writer(f, delimiter=",", quoting=csv.QUOTE_MINIMAL)

    for params in itertools.product(D, P, H, D_MAX):
        for i in range(6):
            instance = (*params, i)
            if instance in already_benchmarked:
                print(
                    f"skipping {instance} since its already present in the comparaison file"
                )
                continue

            print(f"Loading problem {instance}...")
            try:
                problem = FlightProblemMaintenance.from_file(
                    problem_path(*instance), params[3]
                )
                optimal_solution = FlightSolutionMaintenance.from_file(
                    solution_path(*instance), problem
                )
            except Exception as e:
                print(e)
                print(f"couldn't load {instance}, skipping")
                continue

            print("Benchmarking ReducedFlowSolver")
            reduced_results = benchmark_solver(
                reduced_solver,
                problem,
                optimal_solution,
                "reduced_flow_maintnance",
                instance,
            )

            writer.writerow(
                [
                    *instance,
                    reduced_results.execution_time,
                    reduced_results.cost,
                    reduced_results.gap,
                    reduced_results.relative_gap,
                    reduced_results.valid,
                    reduced_results.optimal,
                ]
            )

            f.flush()
