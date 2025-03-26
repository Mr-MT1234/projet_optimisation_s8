import itertools
import bisect

import gurobipy as gp

from flight_optimizer.flight_problem import FlightProblem, FlightProblemMaintenance
from flight_optimizer.solution import FlightSolution, FlightSolutionMaintenance
from .solver import Solver
from ..graph_utils import inverse_graph
from ..commun import *


class ReducedFlowSolver(Solver):
    def solve(self, problem: FlightProblem, timeout=None) -> FlightSolution:
        flight_count = len(problem.flights)
        aircraft_count = len(problem.aircrafts)

        departure_map, arrival_map = self._construct_flight_maps(problem)

        model = gp.Model()
        if timeout:
            model.params.TimeLimit = timeout

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
        The incoming flow to a node can not exceed the outgoing flow 
        """
        for aircraft, airport in itertools.product(problem.aircrafts, problem.airports):
            incoming = arrival_map[airport.id]
            outgoing = departure_map[airport.id]

            i = 0
            j = 0
            incoming_var = aircraft.starting_airport == airport
            outgoing_var = 0
            while i < len(outgoing):
                last_outgoing = outgoing[i]
                while (
                    i < len(outgoing)
                    and outgoing[i].departure_time == last_outgoing.departure_time
                ):
                    outgoing_var += x[outgoing[i].id - 1, aircraft.id]
                    i += 1

                while (
                    j < len(incoming)
                    and last_outgoing.departure_time >= incoming[j].arrival_time
                ):
                    incoming_var += x[incoming[j].id - 1, aircraft.id]
                    j += 1

                model.addConstr(incoming_var - outgoing_var >= 0)

        model.update()
        model.optimize()

        if model.Status == gp.GRB.INFEASIBLE or (
            model.Status == gp.GRB.TIME_LIMIT and model.SolCount == 0
        ):
            return None

        assignment = {aircraft.id: [] for aircraft in problem.aircrafts}

        for flight, aircraft in zip(problem.flights, x.x.argmax(axis=1)):
            assignment[aircraft].append(flight.id)

        return FlightSolution.from_assignment(assignment, problem)

    def solve_maintenance(
        self, problem: FlightProblemMaintenance, timeout=None
    ) -> FlightSolutionMaintenance:
        flight_count = len(problem.flights)
        aircraft_count = len(problem.aircrafts)
        day_count = len(problem.days)
        maintenance_airport_count = len(problem.airports_maintenance)

        departure_map, arrival_map = self._construct_flight_maps(problem)

        model = gp.Model()
        if timeout:
            model.params.TimeLimit = timeout

        x = model.addMVar((flight_count, aircraft_count), vtype=gp.GRB.BINARY)
        z = model.addMVar(
            (aircraft_count, maintenance_airport_count, day_count), vtype=gp.GRB.BINARY
        )
        variable_count = (
            flight_count * aircraft_count
            + aircraft_count * maintenance_airport_count * day_count
        )
        print(f"number of decision variables : {variable_count}")

        # Constraints
        """
        Each flight must be assigned exactly one plaine
        """
        model.addConstr(x.sum(axis=1) == 1)

        """
        The incoming flow to a node can not exceed the outgoing flow 
        """
        for aircraft, airport in itertools.product(problem.aircrafts, problem.airports):
            outgoing_flights = departure_map[airport.id]

            departure_instants = {f.departure_time for f in outgoing_flights}

            for t in departure_instants:
                model.addConstr(
                    self._E(aircraft, airport, t, departure_map, arrival_map, x) >= 0
                )

        """
        Each aircraft must have at least one maintenance every `problem.max_maintenace_delay` days
        """
        for day, day_p in zip(
            problem.days, problem.days[problem.max_maintenace_delay :]
        ):
            model.addConstr(z[:, :, day:day_p].sum(axis=2).sum(axis=1) >= 1)

        """
        Each maintenace airport cannot have more than `problem.capacity_maintenance` aircrafts in a giving day
        """
        model.addConstr(z.sum(axis=0) <= problem.capacity_maintenance)

        """
        For an aircraft to perform a maintenance at and airport a:
        - it must present in the airport a for at least one instant during the maintenance
        """
        for aircraft, (airport_id, airport) in itertools.product(
            problem.aircrafts, enumerate(problem.airports_maintenance)
        ):
            arrival_instants = {f.arrival_time for f in arrival_map[airport.id]}
            for day in problem.days:
                maintenance_strat, maintenance_end = problem.get_maintenance_interval(
                    day
                )
                arrival_instants_during_maintenance = {
                    t
                    for t in arrival_instants
                    if maintenance_strat <= t <= maintenance_end
                }

                exists_during_maintenance = sum(
                    self._E(aircraft, airport, t, departure_map, arrival_map, x)
                    for t in arrival_instants_during_maintenance
                )
                model.addConstr(
                    exists_during_maintenance >= z[aircraft.id, airport_id, day]
                )

        # Objective
        objective = (x * problem.flight_costs).sum() + (
            z.sum(axis=2) * problem.maintenance_costs
        ).sum()
        model.setObjective(objective, gp.GRB.MINIMIZE)

        model.update()
        model.optimize()

        if model.Status == gp.GRB.INFEASIBLE or (
            model.Status == gp.GRB.TIME_LIMIT and model.SolCount == 0
        ):
            return None

        if model.Status == gp.GRB.INFEASIBLE:
            print("Warning: the problem is infeasable")
            return None

        assignment = {aircraft.id: [] for aircraft in problem.aircrafts}
        maintenances = {aircraft.id: [] for aircraft in problem.aircrafts}

        for flight, aircraft in zip(problem.flights, x.x.argmax(axis=1)):
            assignment[aircraft].append(flight.id)

        for aircraft in problem.aircrafts:
            for i, d in itertools.product(
                range(maintenance_airport_count), problem.days
            ):
                if z.x[aircraft.id, i, d] > 0.1:
                    maintenances[aircraft.id].append(
                        (d, problem.airports_maintenance[i])
                    )

        return FlightSolutionMaintenance.from_assignment(
            assignment, maintenances, problem
        )

    def _construct_flight_maps(self, problem: FlightProblem | FlightProblemMaintenance):
        departure_map = {airport.id: [] for airport in problem.airports}
        arrival_map = {airport.id: [] for airport in problem.airports}

        for flight in problem.flights:
            departure_map[flight.departure_airport.id].append(flight)
            arrival_map[flight.arrival_airport.id].append(flight)

        for flights in departure_map.values():
            flights.sort(key=lambda x: x.departure_time)

        for flights in arrival_map.values():
            flights.sort(key=lambda x: x.arrival_time)

        return departure_map, arrival_map

    def _E(
        self, plane: Aircraft, airport: Airport, t: int, departure_map, arrival_map, x
    ):
        outgoing_flights: list[Flight] = departure_map[airport.id]
        incoming_flights: list[Flight] = arrival_map[airport.id]

        incoming_var = plane.starting_airport == airport
        outgoing_var = 0

        i = 0
        while i < len(incoming_flights) and incoming_flights[i].arrival_time <= t:
            incoming_var += x[incoming_flights[i].id - 1, plane.id]
            i += 1

        j = 0
        while j < len(outgoing_flights) and outgoing_flights[j].departure_time <= t:
            outgoing_var += x[outgoing_flights[j].id - 1, plane.id]
            j += 1

        return incoming_var - outgoing_var
