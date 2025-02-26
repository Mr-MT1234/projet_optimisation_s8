import numpy as np
from .commun import *


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
        InitialPositions = {
            int(i[0]):  i[1] for i in InitialPositions
        }

    airports_map = {name: Airport(id=i, name=name) for i, name in enumerate(Airports)}
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

    return FlightProblem(airports, aircrafts, flights, flight_costs)
