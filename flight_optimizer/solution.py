from dataclasses import dataclass
from .commun import *
from .flight_problem import FlightProblem, FlightProblemMaintenance
from .parsing import parse_solution, parse_solution_with_maintenance


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
        
@dataclass
class FlightSolutionMaintenance:
    airports: list[Airport]
    aircrafts: list[Aircraft]
    flights: list[Flight]
    flight_costs: np.ndarray
    maintenance_costs: np.ndarray

    assignment: dict[int, list[Flight]]
    maintenances : dict[int, list[tuple[int, Airport]]]
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
        )

    @classmethod
    def from_assignment(cls, assignment: dict[int, list[int]], maintenances: dict[int, list[tuple[int, Airport]]], problem: FlightProblemMaintenance):
        cost = 0

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
        )
    
