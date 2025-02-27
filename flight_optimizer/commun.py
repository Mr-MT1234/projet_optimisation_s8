from dataclasses import dataclass
import numpy as np


@dataclass
class Airport:
    id: int
    name: str


@dataclass
class Flight:
    id: int
    departure_airport: Airport
    arrival_airport: Airport
    departure_time: int
    arrival_time: int


@dataclass
class Aircraft:
    id: int
    starting_airport: Airport


@dataclass
class FlightProblem:
    airports: list[Airport]
    aircrafts: list[Aircraft]
    flights: list[Flight]
    flight_costs: np.ndarray

    def get_instants(self) -> list[int]:
        departure_instants = [flight.departure_time for flight in self.flights]
        arrival_instants = [flight.arrival_time for flight in self.flights]
        instants = list(sorted(set(arrival_instants + departure_instants)))
        return instants

@dataclass
class FlightSolution:
    airports: list[Airport]
    aircrafts: list[Aircraft]
    assignment: dict[int, list[Flight]] 

    def get_instants(self) -> list[int]:
        departure_instants = [flight.departure_time for flights in self.assignment.values() for flight in flights]
        arrival_instants = [flight.arrival_time for flights in self.assignment.values() for flight in flights]
        instants = list(sorted(set(arrival_instants + departure_instants)))
        return instants

    def __str__(self):
        output = ''
        for aircraft, flights in self.assignment.items():
            output += (f"Flights assigned to aircraft {aircraft}\n")
            flights.sort(key=lambda x: x.departure_time)
            for flight in flights:
                output += (f"\t Flight {flight.id} from {flight.departure_airport} to {flight.arrival_airport} ({flight.departure_time} - {flight.arrival_time})\n")
        
        return output
    
    @classmethod
    def load_from_txt(cls, path, problem: FlightProblem):
        with open(path, 'r') as f:
            assignment = {a.id: [] for a in problem.aircrafts}
            current_aircraft = None
            for line in f:
                if line.startswith("**********Flights assigned to aircraft"):
                    splited = line.strip("*").split(" ")
                    current_aircraft = int(splited[4])
                elif line.startswith("Flight n"):
                    start = line.find('<') + 1
                    end = line.find(' ', start)
                    flight_id = int(line[start:end])
                    assignment[current_aircraft].append(problem.flights[flight_id -1])

        return FlightSolution(
            airports=problem.airports,
            aircrafts=problem.aircrafts,
            assignment=assignment
        )