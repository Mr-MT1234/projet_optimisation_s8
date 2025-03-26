from dataclasses import dataclass
from .commun import *
from .flight_problem import FlightProblem, FlightProblemMaintenance
from .parsing import parse_solution, parse_solution_with_maintenance

import itertools


@dataclass
class FlightSolution:
    airports: list[Airport]
    aircrafts: list[Aircraft]
    flights: list[Flight]
    flight_costs: np.ndarray

    assignment: dict[int, list[Flight]]
    cost: float

    def get_instants(self) -> list[int]:
        departure_instants = [
            flight.departure_time
            for flights in self.assignment.values()
            for flight in flights
        ]
        arrival_instants = [
            flight.arrival_time
            for flights in self.assignment.values()
            for flight in flights
        ]
        instants = list(sorted(set(arrival_instants + departure_instants)))
        return instants

    def __str__(self):
        output = ""
        for aircraft, flights in self.assignment.items():
            output += f"Flights assigned to aircraft {aircraft}\n"
            flights.sort(key=lambda x: x.departure_time)
            for flight in flights:
                output += f"\t Flight {flight.id} from {flight.departure_airport.name} to {flight.arrival_airport.name} ({flight.departure_time} - {flight.arrival_time})\n"

        return output

    @classmethod
    def from_file(cls, path: str, problem: FlightProblem):
        assignment = parse_solution(path)

        cost = 0.0

        for i, flights in assignment.items():
            cost += sum(problem.flight_costs[flight_id - 1, i] for flight_id in flights)

        assignment_flights = {aircraft.id: [] for aircraft in problem.aircrafts}

        for i, flights in assignment.items():
            for flight in flights:
                assignment_flights[i].append(problem.flights[flight - 1])

        return cls(
            airports=problem.airports,
            aircrafts=problem.aircrafts,
            flights=problem.flights,
            flight_costs=problem.flight_costs,
            assignment=assignment_flights,
            cost=cost,
        )

    @classmethod
    def from_assignment(cls, assignment: dict[int, list[int]], problem: FlightProblem):
        cost = 0

        for i, flights in assignment.items():
            cost += sum(problem.flight_costs[flight_id - 1, i] for flight_id in flights)

        assignment_flights = {aircraft.id: [] for aircraft in problem.aircrafts}

        for i, flights in assignment.items():
            for flight in flights:
                assignment_flights[i].append(problem.flights[flight - 1])

        return cls(
            airports=problem.airports,
            aircrafts=problem.aircrafts,
            flights=problem.flights,
            flight_costs=problem.flight_costs,
            assignment=assignment_flights,
            cost=cost,
        )

    def is_valide(self) -> tuple[bool, str]:
        for aircraft in self.aircrafts:
            flights: list[Flight] = self.assignment[aircraft.id]
            flights = sorted(flights, key=lambda x: x.departure_time)

            # Check if consecutive flights are compatible i.e, no simultaneous flights and airport continuity is verified
            for f1, f2 in zip(flights, flights[1:]):
                if f1.arrival_time > f2.departure_time:
                    return (
                        False,
                        f"The assignment contains two simultaneous flights for the aircraft {aircraft.id} (flights {f1.id} and {f2.id})",
                    )

                if f1.arrival_airport != f2.departure_airport:
                    return (
                        False,
                        f"The assignment contains two consucative flights with incompatible airports for the aircraft {aircraft.id} (flights {f1.id} and {f2.id})",
                    )

            # Check that aircraft start at the correct airport
            initial_flight = flights[0]
            if initial_flight.departure_airport != aircraft.starting_airport:
                return (
                    False,
                    f"The assignment requires the aircraft {aircraft.id} starts from airport {initial_flight.departure_airport}, but it start at {aircraft.starting_airport} ",
                )

        # Check all flight where assigned
        flight_exits = [False] * len(self.flights)
        for flights in self.assignment.values():
            for f in flights:
                flight_exits[f.id - 1] = True

        if not all(flight_exits):
            return (
                False,
                f"Flights { [flight.id for flight in self.flights if not flight_exits[flight.id - 1] ] } were not served",
            )

        return (True, "Everything is fine")


@dataclass
class FlightSolutionMaintenance:

    airports: list[Airport]
    aircrafts: list[Aircraft]
    flights: list[Flight]
    flight_costs: np.ndarray
    maintenance_costs: np.ndarray
    max_maintenace_delay: int
    days: list[int]

    assignment: dict[int, list[Flight]]
    maintenances: dict[int, list[tuple[int, Airport]]]
    cost: float

    def get_maintenance_interval(self, day: int) -> tuple[int, int]:
        start_hour = 22
        end_hour = 24 + 6
        return (60 * start_hour + 60 * 24 * day, 60 * end_hour + 60 * 24 * day)

    def get_instants(self) -> list[int]:
        departure_instants = [
            flight.departure_time
            for flights in self.assignment.values()
            for flight in flights
        ]
        arrival_instants = [
            flight.arrival_time
            for flights in self.assignment.values()
            for flight in flights
        ]
        instants = list(sorted(set(arrival_instants + departure_instants)))
        return instants

    def __str__(self):
        output = ""
        for aircraft, flights in self.assignment.items():
            output += f"Flights assigned to aircraft {aircraft}\n"
            flights.sort(key=lambda x: x.departure_time)
            for flight in flights:
                output += f"\t Flight {flight.id} from {flight.departure_airport.name} to {flight.arrival_airport.name} ({flight.departure_time} - {flight.arrival_time})\n"

        return output

    @classmethod
    def from_file(cls, path: str, problem: FlightProblemMaintenance):
        assignment, maintenances = parse_solution_with_maintenance(path)

        cost = 0.0

        for i, flights in assignment.items():
            cost += sum(problem.flight_costs[flight_id - 1, i] for flight_id in flights)
        for i, maintenance in maintenances.items():
            for day, airport in maintenance:
                airport = next(a for a in problem.airports if a.name == airport)
                index_airport = problem.airports_maintenance.index(airport)
                cost += problem.maintenance_costs[i, index_airport]

        assignment_flights = {aircraft.id: [] for aircraft in problem.aircrafts}

        for i, flights in assignment.items():
            for flight in flights:
                assignment_flights[i].append(problem.flights[flight - 1])

        maintenance_flights = {aircraft.id: [] for aircraft in problem.aircrafts}

        for i, maintenance in maintenances.items():
            for day, airport in maintenance:
                airport = next(a for a in problem.airports if a.name == airport)
                maintenance_flights[i].append((day, airport))

        return cls(
            airports=problem.airports,
            aircrafts=problem.aircrafts,
            flights=problem.flights,
            flight_costs=problem.flight_costs,
            maintenance_costs=problem.maintenance_costs,
            assignment=assignment_flights,
            maintenances=maintenance_flights,
            cost=cost,
            max_maintenace_delay=problem.max_maintenace_delay,
            days=problem.days,
        )

    @classmethod
    def from_assignment(
        cls,
        assignment: dict[int, list[int]],
        maintenances: dict[int, list[tuple[int, Airport]]],
        problem: FlightProblemMaintenance,
    ):
        cost = 0

        for i, flights in assignment.items():
            cost += sum(problem.flight_costs[flight_id - 1, i] for flight_id in flights)
        for i, maintenance in maintenances.items():
            for day, airport in maintenance:
                airport = next(a for a in problem.airports if a == airport)
                index_airport = problem.airports_maintenance.index(airport)
                cost += problem.maintenance_costs[i, index_airport]

        assignment_flights = {aircraft.id: [] for aircraft in problem.aircrafts}

        for i, flights in assignment.items():
            for flight in flights:
                assignment_flights[i].append(problem.flights[flight - 1])

        maintenance_flights = {aircraft.id: [] for aircraft in problem.aircrafts}

        for i, maintenance in maintenances.items():
            for day, airport in maintenance:
                airport = next(a for a in problem.airports if a == airport)
                maintenance_flights[i].append((day, airport))

        return cls(
            airports=problem.airports,
            aircrafts=problem.aircrafts,
            flights=problem.flights,
            flight_costs=problem.flight_costs,
            maintenance_costs=problem.maintenance_costs,
            assignment=assignment_flights,
            maintenances=maintenance_flights,
            cost=cost,
            max_maintenace_delay=problem.max_maintenace_delay,
            days=problem.days,
        )

    def is_valide(self) -> tuple[bool, str]:
        for aircraft in self.aircrafts:
            flights: list[Flight] = self.assignment[aircraft.id]
            flights = sorted(flights, key=lambda x: x.departure_time)
            maintenances = sorted(
                self.maintenances[aircraft.id]
            )  # sort maintenances by day

            # Check if consecutive flights are compatible i.e, no simultaneous flights and airport continuity is verified
            for f1, f2 in zip(flights, flights[1:]):
                if f1.arrival_time > f2.departure_time:
                    return (
                        False,
                        f"The assignment contains two simultaneous flights for the aircraft {aircraft.id} (flights {f1.id} and {f2.id})",
                    )

                if f1.arrival_airport != f2.departure_airport:
                    return (
                        False,
                        f"The assignment contains two consecutive flights with incompatible airports for the aircraft {aircraft.id} (flights {f1.id} and {f2.id})",
                    )

            # Check that aircraft start at the correct airport
            initial_flight = flights[0]
            if initial_flight.departure_airport != aircraft.starting_airport:
                return (
                    False,
                    f"The assignment requires the aircraft {aircraft.id} starts from airport {initial_flight.departure_airport}, but it start at {aircraft.starting_airport} ",
                )

            # Check that the aircraft has a maintenance at least once every d_max days
            maintenance_days = (
                [self.days[0]] + [day for day, _ in maintenances] + [self.days[-1]]
            )

            for day, day_p in zip(maintenance_days, maintenance_days[1:]):
                if day_p - day > self.max_maintenace_delay:
                    return (
                        False,
                        f"Aircraft {aircraft.id} does not satisfy maintenance constraints, found difference of {day_p - day} days",
                    )

            # Check that all the assigned maintenances are compatible with the flight, i.e the aircraft will be at the right airport during the maintenance
            current_instant = 0
            current_airport = aircraft.starting_airport
            current_maintenance = 0
            for flight in flights:
                if current_maintenance >= len(maintenances):
                    break

                maintenance_day, maintenance_airport = maintenances[current_maintenance]
                maintenance_start, maintenance_end = self.get_maintenance_interval(
                    maintenance_day
                )
                if current_airport == maintenance_airport and (
                    current_instant <= maintenance_start <= flight.departure_time
                    or current_instant <= maintenance_end <= flight.departure_time
                    or maintenance_start <= current_instant <= maintenance_end
                ):
                    current_maintenance += 1

                current_airport = flight.arrival_airport
                current_instant = flight.arrival_time

            if current_maintenance < len(maintenances):
                return (
                    False,
                    f"Aircraft {aircraft.id} cannot satisfy the maintenance {maintenances[current_maintenance]}",
                )

        # Check that all flights were served
        flight_exits = [False] * len(self.flights)

        for flights in self.assignment.values():
            for f in flights:
                flight_exits[f.id - 1] = True

        if not all(flight_exits):
            return (
                False,
                f"Flights { [flight.id for flight in self.flights if not flight_exits[flight.id - 1] ] } were not served",
            )

        return (True, "Everything is fine")
