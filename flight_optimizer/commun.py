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


@dataclass
class FlightSolution:
    assignment: dict[int, list[Flight]] 

    def __str__(self):
        output = ''
        for aircraft, flights in self.assignment.items():
            output += (f"Flights assigned to aircraft {aircraft}\n")
            flights.sort(key=lambda x: x.departure_time)
            for flight in flights:
                output += (f"\t Flight {flight.id} from {flight.departure_airport} to {flight.arrival_airport} ({flight.departure_time} - {flight.arrival_time})\n")
        
        return output