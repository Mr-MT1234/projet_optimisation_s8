import numpy as np
from dataclasses import dataclass


@dataclass
class Airport:
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


def parse_problem(filepath: str) -> FlightProblem:
    with open(filepath, "r") as file:
        data = file.read().split(";\n")
        Airports = data[0].replace("Airports =  ", "").strip("{}").split(",")[:-1]

        NbFlights = int(data[1].replace("Nbflight = ", ""))

        Aircrafts = [
            int(i)
            for i in data[2].replace("Aircrafts = ", "").strip("{}").split(",")[:-1]
        ]

        Flights = data[3].replace("Flight = ", "").strip("{}").split("\n")[1:]
        Flights = [i.strip("<>").split(",") for i in Flights]
        Flights = [
            {
                "id": int(i[0]),
                "origin": i[1],
                "destination": i[2],
                "departure": float(i[3]),
                "arrival": float(i[4]),
            }
            for i in Flights
        ]

        Cost = data[4].replace("Cost =", "").strip("[]").split("\n")[1:-1]
        Cost = [i.strip("[]").split(",")[:-1] for i in Cost]
        Cost = np.array([[float(j) for j in i] for i in Cost])

        InitialPositions = (
            data[5].replace("Aircraft = \n", "").strip(";").strip("[]").split(" ,")[:-1]
        )
        InitialPositions = [i.strip("<>").split(",") for i in InitialPositions]
        InitialPositions = [
            {"id": int(i[0]), "airport": i[1]} for i in InitialPositions
        ]

    airports = [Airport(name=name) for name in Airports]
    aircrafts = [
        Aircraft(
            id=aircraft_id, 
            starting_airport=Airport(InitialPositions[aircraft_id]['airport'])
        )
        for aircraft_id in Aircrafts
    ]
    flights = [
        Flight(
            id=flight["id"],
            departure_airport=Airport(flight["origin"]),
            arrival_airport=Airport(flight["destination"]),
            departure_time=int(flight["departure"]),
            arrival_time=int(flight["arrival"]),
        )
        for flight in Flights
    ]

    flight_costs = Cost

    return FlightProblem(
        airports,
        aircrafts,
        flights,
        flight_costs
    )
