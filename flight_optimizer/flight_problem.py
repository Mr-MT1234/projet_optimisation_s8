from dataclasses import dataclass
from .commun import *
from .parsing import parse_problem


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

    @classmethod
    def from_file(cls, path: str) -> "FlightProblem":
        Airports, Aircrafts, Flights, Cost, InitialPositions = parse_problem(path)

        airports_map = {
            name: Airport(id=i, name=name) for i, name in enumerate(Airports)
        }
        airports = [airports_map[name] for name in Airports]
        aircrafts = [
            Aircraft(
                id=aircraft_id,
                starting_airport=airports_map[airport_name],
            )
            for aircraft_id, airport_name in InitialPositions.items()
        ]
        flights = [
            Flight(
                id=flight["id"],
                departure_airport=airports_map[flight["origin"]],
                arrival_airport=airports_map[flight["destination"]],
                departure_time=int(flight["departure"]),
                arrival_time=int(flight["arrival"]),
            )
            for flight in Flights
        ]

        flight_costs = Cost

        return cls(airports, aircrafts, flights, flight_costs)
