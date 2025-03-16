import itertools
import bisect

import gurobipy as gp

from flight_optimizer.flight_problem import FlightProblem, FlightProblemMaintenance
from flight_optimizer.solution import FlightSolution
from .solver import Solver
from ..graph_utils import inverse_graph
from ..commun import *


class ReducedFlowSolver(Solver):
    def solve(self, problem: FlightProblem) -> FlightSolution:
        flight_count = len(problem.flights)
        aircraft_count = len(problem.aircrafts)

        arrival_graph = {flight.id: [] for flight in problem.flights}

        for flight1, flight2 in itertools.combinations(problem.flights, 2):
            if (
                flight2.arrival_airport == flight1.departure_airport
                and flight2.arrival_time <= flight1.departure_time
            ):
                arrival_graph[flight1.id].append(flight2.id)
            if (
                flight1.arrival_airport == flight2.departure_airport
                and flight1.arrival_time <= flight2.departure_time
            ):
                arrival_graph[flight2.id].append(flight1.id)

        departure_graph = {flight.id: [] for flight in problem.flights}

        for flight1, flight2 in itertools.combinations(problem.flights, 2):
            if (
                flight1.departure_airport == flight2.departure_airport
                and flight1.departure_time >= flight2.departure_time
            ):
                departure_graph[flight1.id].append(flight2.id)
            if (
                flight2.departure_airport == flight1.departure_airport
                and flight2.departure_time >= flight1.departure_time
            ):
                departure_graph[flight2.id].append(flight1.id)

        model = gp.Model()

        x = model.addMVar((flight_count, aircraft_count), vtype=gp.GRB.BINARY)
        variable_count = flight_count * aircraft_count
        print(f"number of decision variables : {variable_count}")

        # Objective
        objective = (x * problem.flight_costs).sum()
        model.setObjective(objective, gp.GRB.MINIMIZE)

        # Constraints
        """
        Each flight must be assigned exactly one plaine
        """
        model.addConstr(x.sum(axis=1) == 1)

        """
        The incoming flow to a node can not exceed the out going flow 
        TODO change
        """
        for aircraft in problem.aircrafts:
            for flight in problem.flights:
                departures_indices = [id - 1 for id in departure_graph[flight.id]]
                arrivals_indices = [id - 1 for id in arrival_graph[flight.id]]

                currently_in_airport = (
                    x[arrivals_indices, aircraft.id].sum()
                    - x[departures_indices, aircraft.id].sum()
                )

                if flight.departure_airport == aircraft.starting_airport:
                    model.addConstr(
                        currently_in_airport + 1 >= x[flight.id - 1, aircraft.id]
                    )
                else:
                    model.addConstr(
                        currently_in_airport >= x[flight.id - 1, aircraft.id]
                    )

        model.update()
        model.optimize()

        assignment = {aircraft.id: [] for aircraft in problem.aircrafts}

        for flight, aircraft in zip(problem.flights, x.x.argmax(axis=1)):
            assignment[aircraft].append(flight.id)

        return FlightSolution.from_assignment(assignment, problem)

    def solve_maintenance(self, problem: FlightProblemMaintenance):
        flight_count = len(problem.flights)
        aircraft_count = len(problem.aircrafts)
        maintenance_airports_count = len(problem.airports_maintenance)
        day_count = len(problem.days)

        arrival_graph = {flight.id: [] for flight in problem.flights}

        for flight1, flight2 in itertools.combinations(problem.flights, 2):
            if (
                flight2.arrival_airport == flight1.departure_airport
                and flight2.arrival_time <= flight1.departure_time
            ):
                arrival_graph[flight1.id].append(flight2.id)
            if (
                flight1.arrival_airport == flight2.departure_airport
                and flight1.arrival_time <= flight2.departure_time
            ):
                arrival_graph[flight2.id].append(flight1.id)

        departure_graph = {flight.id: [] for flight in problem.flights}

        for flight1, flight2 in itertools.combinations(problem.flights, 2):
            if (
                flight1.departure_airport == flight2.departure_airport
                and flight1.departure_time >= flight2.departure_time
            ):
                departure_graph[flight1.id].append(flight2.id)
            if (
                flight2.departure_airport == flight1.departure_airport
                and flight2.departure_time >= flight1.departure_time
            ):
                departure_graph[flight2.id].append(flight1.id)

        model = gp.Model()

        x = model.addMVar((flight_count, aircraft_count), vtype=gp.GRB.BINARY)
        z = model.addMVar(
            (aircraft_count, maintenance_airports_count, day_count), vtype=gp.GRB.BINARY
        )

        # Constraints
        """
        Each flight must be assigned exactly one plaine
        """
        model.addConstr(x.sum(axis=1) == 1)

        """
        The incoming flow to a node can not exceed the out going flow 
        TODO change
        """
        for aircraft in problem.aircrafts:
            for flight in problem.flights:
                currently_in_airport = self.__present_at(
                    aircraft,
                    flight.departure_airport,
                    flight.departure_time,
                    x,
                    departure_map,
                    arrival_map,
                )
                model.addConstr(currently_in_airport >= x[flight.id - 1, aircraft.id])


        for day in problem.days[:problem.m]:
            d
        return
