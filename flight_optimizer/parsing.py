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
        InitialPositions = {int(i[0]): i[1] for i in InitialPositions}

    return Airports, Aircrafts, Flights, Cost, InitialPositions

def parse_problem_with_maintenance(filepath: str):
    with open(filepath, 'r') as file:
        data = file.read().split(";\n")
        Airports = data[0].replace("Airports =  ", "").strip("{}").split(",")[:-1]
        
        AirportMaintenance = data[1].replace("Airportmaintenance =  ", "").strip("{}").split(",")[:-1]
        
        NbFlights = int(data[2].replace("Nbflight = ", ""))

        Aircrafts = [
            int(i)
            for i in data[3].replace("Aircrafts = ", "").strip("{}").split(",")[:-1]
        ]
        
        Days = [
            int(i)
            for i in data[4].replace("Days =  ", "").strip("{}").split(",")
        ]

        Flights = data[5].replace("Flight = ", "").strip("{}").split("\n")[1:]
        Flights = [i.strip("<>").split(",") for i in Flights]
        Flights = [
            {
                "id": int(i[0]),
                "origin": i[1],
                "destination": i[2],
                "departure": float(i[3]),
                "arrival": float(i[4]),
                "day": int(i[5])
            }
            for i in Flights
        ]

        Cost = data[6].replace("Cost =", "").strip("[]").split("\n")[1:-1]
        Cost = [i.strip("[]").split(",")[:-1] for i in Cost]
        Cost = np.array([[float(j) for j in i] for i in Cost])
        
        CostMaintenance = data[7].replace("CostMaintenance = ", "").strip("[]").split("\n")[1:-1]
        CostMaintenance = [i.strip("[]").split(",")[:-1] for i in CostMaintenance]
        CostMaintenance = np.array([[float(j) for j in i] for i in CostMaintenance])

        CapacityMaintenance = int(data[8].replace("capmaintenance =", ""))
        
        horizon = int(data[9].replace("horizon =", ""))
        
        InitialPositions = (
            data[10].replace("Aircraft = \n", "").strip(";").strip("[]").split(" ,")[:-1]
        )
        InitialPositions = [i.strip("<>").split(",") for i in InitialPositions]
        InitialPositions = {int(i[0]): i[1] for i in InitialPositions}

    return Airports, Aircrafts, Flights, Cost, InitialPositions, AirportMaintenance, Days, CostMaintenance, CapacityMaintenance

def parse_solution(path):
    assignment = {}

    with open(path, "r", encoding = "ISO-8859-1") as f:
        current_aircraft = None
        for line in f:
            if line.startswith("**********Flights assigned to aircraft"):
                splited = line.strip("*").split(" ")
                current_aircraft = int(splited[4])
            elif line.startswith("Flight n"):
                start = line.find("<") + 1
                end = line.find(" ", start)
                flight_id = int(line[start:end])
                assignment.setdefault(current_aircraft, []).append(flight_id)

    return assignment

def parse_solution_with_maintenance(path):
    assignment = {}
    maintenance = {}

    with open(path, "r", encoding = "ISO-8859-1") as f:
        current_aircraft = None
        for line in f:
            if line.startswith("**********Flights assigned to aircraft"):
                splited = line.strip("*").split(" ")
                current_aircraft = int(splited[4])
            elif line.startswith("Flight n"):
                start = line.find("<") + 1
                end = line.find(" ", start)
                flight_id = int(line[start:end])
                assignment.setdefault(current_aircraft, []).append(flight_id)
            elif line.startswith("Plane"):
                splited = line.split(" ")
                current_aircraft = int(splited[1])
            elif line.startswith("( "):
                splited = line.strip("()").split(" ")
                maintenance.setdefault(current_aircraft, []).append((splited[1],splited[4]))
                
    return assignment, maintenance