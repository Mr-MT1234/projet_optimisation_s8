from flight_optimizer.parsing import parse_problem

parsed = parse_problem("./data/d=1/p=20/h=15/DataCplex_density=1_p=20_h=15_test_0.dat")

print(parsed.flight_costs.shape)

