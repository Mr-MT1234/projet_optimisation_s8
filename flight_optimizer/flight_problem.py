from dataclasses import dataclass
from .commun import *
from .parsing import parse_problem, parse_problem_with_maintenance


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
                day=int(flight["departure"] // (60*24)),
            )
            for flight in Flights
        ]

        flight_costs = Cost

        return cls(airports, aircrafts, flights, flight_costs)

@dataclass
class FlightProblemMaintenance:
    airports: list[Airport]
    airports_maintenance: list[Airport]
    aircrafts: list[Aircraft]
    flights: list[Flight]
    days: list[int]
    flight_costs: np.ndarray
    maintenance_costs: np.ndarray
    capacity_maintenance: int

    def get_instants(self) -> list[int]:
        departure_instants = [flight.departure_time for flight in self.flights]
        arrival_instants = [flight.arrival_time for flight in self.flights]
        instants = list(sorted(set(arrival_instants + departure_instants)))
        return instants

    @classmethod
    def from_file(cls, path: str) -> "FlightProblem":
        Airports, Aircrafts, Flights, Cost, InitialPositions, AirportMaintenance, Days, CostMaintenance, CapacityMaintenance = parse_problem_with_maintenance(path)

        airports_map = {
            name: Airport(id=i, name=name) for i, name in enumerate(Airports)
        }
        airports = [airports_map[name] for name in Airports]
        airports_maintenance = [airports_map[name] for name in AirportMaintenance]
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
                day=int(flight["day"]),
            )
            for flight in Flights
        ]

        flight_costs = Cost
        maintenance_costs = CostMaintenance
        capacity_maintenance = CapacityMaintenance
        days = Days

        return cls(airports, airports_maintenance, aircrafts, flights, days, flight_costs, maintenance_costs, capacity_maintenance)