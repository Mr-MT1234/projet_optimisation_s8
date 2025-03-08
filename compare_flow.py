import pickle
import os
import argparse
from datetime import datetime
import itertools
import csv
import os

import matplotlib.pyplot as plt

from flight_optimizer import *

OUTPUT_DIR = os.path.join(os.getcwd(), "benchmarks/flow_comparaison30")


def problem_path(d: float, p: int, h: int, test_index: int):
    return f"./data/d={d}/p={p}/h={h}/DataCplex_density={d}_p={p}_h={h}_test_{test_index}.dat"


def solution_path(d: float, p: int, h: int, test_index: int):
    return f"./data/d={d}/p={p}/h={h}/Optimal_Solution_density={d}_p={p}_h={h}_test_{test_index}.txt"


D = [0.5, 0.7, 1.0]
P = [10, 20, 30, 40]
H = [7, 15, 21, 30]


def solve_and_write(density, planes, horizon, index, solver, problem):
    reporter = Reporter()

    match solver:
        case 1:
            solver = FlowSolver()
            method = "flow"
        case 2:
            solver = FlowSolver2()
            method = "flow2"

    correct_solution = FlightSolution.from_file(
        solution_path(density, planes, horizon, index), problem
    )

    start = datetime.now()
    solution = solver.solve(problem)
    end = datetime.now()

    execution_time = (end - start).total_seconds()

    fig = reporter.plot_solution(
        [solution, correct_solution], legend=["Found solution", "Optimal solution"]
    )

    benchmark_dir = f"./benchmarks/{method}"
    output_dir = os.path.join(
        benchmark_dir,
        f"problem_d={density}_p={planes}_h={horizon}_i={index}",
    )

    if not os.path.exists(benchmark_dir):
        os.makedirs(benchmark_dir)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    fig.savefig(os.path.join(output_dir, "visualisation.pdf"), format="pdf")

    plt.close(fig)

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

    return solution


with open(os.path.join(OUTPUT_DIR, "results.csv"), "w", newline='') as outputfile:
    writer = csv.writer(outputfile, delimiter=",", quoting=csv.QUOTE_MINIMAL)
    writer.writerow(
        [
            "density",
            "planes",
            "horizon",
            "index",
            "cost_optimal",
            "cost_flow1",
            "cost_flow2",
            "gap_flow1",
            "gap_flow2",
            "relative_error_flow1 (%)",
            "relative_error_flow2 (%)",
        ]
    )
    for density, planes, horizon, index in itertools.product(D, P, H, range(10)):
        print(f"comparing problem ... {density=}{planes=}{horizon=}{index=}")
        try:
            problem = FlightProblem.from_file(problem_path(density, planes, horizon, index))

            for flight in problem.flights:
                flight.arrival_time += 30

            solution1 = solve_and_write(density, planes, horizon, index, 1, problem)
            solution2 = solve_and_write(density, planes, horizon, index, 2, problem)
            correct_solution = FlightSolution.from_file(
                solution_path(density, planes, horizon, index), problem
            )

            writer.writerow(
                [
                    density,
                    planes,
                    horizon,
                    index,
                    correct_solution.cost,
                    solution1.cost,
                    solution2.cost,
                    solution1.cost - correct_solution.cost,
                    solution2.cost - correct_solution.cost,
                    round((solution1.cost - correct_solution.cost)/correct_solution.cost*100, 2),
                    round((solution2.cost - correct_solution.cost)/correct_solution.cost*100, 2),
                ]
            )
        except Exception as e:
            if isinstance(e, KeyboardInterrupt):
                exit()
            print(f"encountered error")
