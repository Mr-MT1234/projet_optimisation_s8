import numpy as np
from .commun import *


def parse_problem(filepath: str):
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

    return Airports, Aircrafts, Flights, Cost, InitialPositions

def parse_solution(path):
     with open(path, 'r') as f:
            assignment = {}
            current_aircraft = None
            for line in f:
                if line.startswith("**********Flights assigned to aircraft"):
                    splited = line.strip("*").split(" ")
                    current_aircraft = int(splited[4])
                elif line.startswith("Flight n"):
                    start = line.find('<') + 1
                    end = line.find(' ', start)
                    flight_id = int(line[start:end])
                    assignment.setdefault(current_aircraft, []).append(flight_id)

            return assignment
