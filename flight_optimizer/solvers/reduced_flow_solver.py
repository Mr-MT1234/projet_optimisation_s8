import itertools
import bisect

import gurobipy as gp

from flight_optimizer.flight_problem import FlightProblem, FlightProblemMaintenance
from flight_optimizer.solution import FlightSolution, FlightSolutionMaintenance
from .solver import Solver
from ..graph_utils import inverse_graph
from ..commun import *


class ReducedFlowSolver(Solver):
    def solve(self, problem: FlightProblem) -> FlightSolution:
        flight_count = len(problem.flights)
        aircraft_count = len(problem.aircrafts)

        departure_map, arrival_map = self._construct_flight_maps(problem)

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

        assignment = {aircraft.id: [] for aircraft in problem.aircrafts}

        for flight, aircraft in zip(problem.flights, x.x.argmax(axis=1)):
            assignment[aircraft].append(flight.id)

        return FlightSolution.from_assignment(assignment, problem)

    def solve_maintenance(
        self, problem: FlightProblemMaintenance
    ) -> FlightSolutionMaintenance:
        flight_count = len(problem.flights)
        aircraft_count = len(problem.aircrafts)
        day_count = len(problem.days)
        maintenance_airport_count = len(problem.airports_maintenance)

        departure_map, arrival_map = self._construct_flight_maps(problem)

        model = gp.Model()

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
            incoming = arrival_map[airport.id]
            outgoing = departure_map[airport.id]
            
            for day in problem.days:
                i = j = 0
                incoming_var = aircraft.starting_airport == airport
                outgoing_var = 0
                maintenance_start, maintenance_end = problem.get_maintenance_interval(
                    day
                )

                # Add all the flight before the maintenance
                while (
                    i < len(incoming) and incoming[i].arrival_time < maintenance_start
                ):
                    incoming_var += x[incoming[i].id - 1, aircraft.id]
                    i += 1
                while (
                    j < len(outgoing) and outgoing[j].departure_time < maintenance_start
                ):
                    outgoing_var += x[outgoing[j].id - 1, aircraft.id]
                    j += 1

                exists_during_maintenance = 0
                while i < len(incoming) and incoming[i].arrival_time <= maintenance_end:
                    last_incoming = incoming[i]
                    while (
                        i < len(incoming)
                        and incoming[i].arrival_time == last_incoming.arrival_time
                    ):
                        incoming_var += x[incoming[i].id - 1, aircraft.id]
                        i += 1

                    while (
                        j < len(outgoing)
                        and outgoing[j].departure_time <= last_outgoing.arrival_time
                    ):
                        outgoing_var += x[outgoing[j].id - 1, aircraft.id]
                        j += 1

                    exists_during_maintenance += incoming_var - outgoing_var

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
