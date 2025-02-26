from flight_optimizer.parsing import parse_problem
from flight_optimizer.solvers.Interval_solver import IntervalSolver

parsed = parse_problem("./data/d=0.5/p=10/h=7/DataCplex_density=0.5_p=10_h=7_test_0.dat")

solver = IntervalSolver()

solution = solver.solve(parsed)

print(solution)
