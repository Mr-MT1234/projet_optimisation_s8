from dataclasses import dataclass
from .commun import *
from .flight_problem import FlightProblem
from .parsing import parse_solution


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
