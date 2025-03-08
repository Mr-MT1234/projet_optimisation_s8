import itertools

import gurobipy as gp

from flight_optimizer.flight_problem import FlightProblem
from flight_optimizer.solution import FlightSolution
from .solver import Solver
from ..graph_utils import inverse_graph


class FlowSolver(Solver):
    def solve(self, problem: FlightProblem) -> FlightSolution:
        flight_graph = {i: [] for i in range(1, len(problem.flights) + 1)}

        for flight1, flight2 in itertools.combinations(problem.flights, 2):
            if (
                flight1.arrival_airport == flight2.departure_airport
                and flight1.arrival_time <= flight2.departure_time
            ):
                flight_graph[flight1.id].append(flight2.id)
            if (
                flight2.arrival_airport == flight1.departure_airport
                and flight2.arrival_time <= flight1.departure_time
            ):
                flight_graph[flight2.id].append(flight1.id)

        dependency_graph = {
            aircraft.id: {flight: out.copy() for flight, out in flight_graph.items()}
            for aircraft in problem.aircrafts
        }

        for aircraft in problem.aircrafts:
            dependency_graph[aircraft.id][-1] = [
                flight.id
                for flight in problem.flights
                if flight.departure_airport == aircraft.starting_airport
            ]

        dependency_graph_inv = {
            aircraft: inverse_graph(subgraph)
            for aircraft, subgraph in dependency_graph.items()
        }

        model = gp.Model()
        model.params.OutputFlag = 0

        vars = {
            aircraft: {
                flight: [
                    model.addVar(
                        vtype=gp.GRB.BINARY, name=f"x_{aircraft}_{flight}_{flight2}"
                    )
                    for flight2 in out
                ]
                for flight, out in subgraph.items()
            }
            for aircraft, subgraph in dependency_graph.items()
        }

        # Objective
        objective = 0

        for aircraft, subgraph in dependency_graph.items():
            for flight_s, out in subgraph.items():
                for i, flight in enumerate(out):

                    objective += (
                        problem.flight_costs[flight - 1, aircraft]
                        * vars[aircraft][flight_s][i]
                    )

        model.setObjective(objective, gp.GRB.MINIMIZE)

        # Constraints
        """
        Each node must be visited by exactly one plain
        """
        for flight in problem.flights:
            constraint = 0
            for aircraft in problem.aircrafts:
                for flight_p in dependency_graph_inv[aircraft.id][flight.id]:
                    i = dependency_graph[aircraft.id][flight_p].index(flight.id)
                    constraint += vars[aircraft.id][flight_p][i]

            model.addConstr(constraint == 1)

        """
        The incoming flow to a node can not exceed the out going flow
        """
        for flight in problem.flights:
            for aircraft in problem.aircrafts:
                preds = dependency_graph_inv[aircraft.id][flight.id]

                out = sum(vars[aircraft.id][flight.id])
                _in = 0

                for pred in preds:
                    i = dependency_graph[aircraft.id][pred].index(flight.id)
                    x = vars[aircraft.id][pred][i]
                    _in += x

                model.addConstr(_in >= out)

        """
        Each plain can serve at most one flight from its initial position
        """
        for aircraft in problem.aircrafts:
            model.addConstr(sum(vars[aircraft.id][-1]) <= 1)

        model.update()
        model.optimize()

        assignment = {
            aircraft: [
                i
                for flight, out in subgraph.items()
                for i, x in zip(out, vars[aircraft][flight])
                if x.x > 0.0
            ]
            for aircraft, subgraph in dependency_graph.items()
        }

        return FlightSolution.from_assignment(assignment, problem)

