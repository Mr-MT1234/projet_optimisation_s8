import gurobipy as gp
from .solver import Solver
from ..commun import *


class IntervalSolver(Solver):

    def solve(self, problem: FlightProblem) -> FlightSolution:
        instants = self.__get_instants(problem)

        nb_flights = len(problem.flights)
        nb_airports = len(problem.airports)
        nb_aircrafts = len(problem.aircrafts)
        nb_intervals = len(instants) - 1
        nb_instants = len(instants)

        flights_in_interval = [[] for i in range(nb_intervals)]

        for flight in problem.flights:
            departure_instant_index = instants.index(flight.departure_time)
            arrival_instant_index = instants.index(flight.arrival_time)
            for t in range(departure_instant_index, arrival_instant_index):
                flights_in_interval[t].append(flight)

        model = gp.Model()

        x = model.addMVar((nb_flights, nb_aircrafts), vtype=gp.GRB.BINARY, name="x")
        o = model.addMVar((nb_aircrafts, nb_intervals), vtype=gp.GRB.BINARY, name="o")
        a = model.addMVar(
            (nb_aircrafts, nb_airports, nb_instants), vtype=gp.GRB.BINARY, name="a"
        )

        model.setObjective((x * problem.flight_costs).sum(), gp.GRB.MINIMIZE)

        """
        Each flight is served by exactly one plane
        """
        model.addConstr(x.sum(axis=1) == 1)

        """
        If plane p serve the flight f, then:
        - p must be at the departure airport of f at the time of departure
        - p must be at the arrival airport of f at the time of arrival
        - p must not be present on any airports during the flight
        - p is occupied during the flight
        """

        for flight_index, flight in enumerate(problem.flights):
            for aircraft in problem.aircrafts:
                departure_instant_index = instants.index(flight.departure_time)
                arrival_instant_index = instants.index(flight.arrival_time)

                departure_airport, arrival_airport = (
                    flight.departure_airport,
                    flight.arrival_airport,
                )

                model.addConstr(
                    a[aircraft.id, departure_airport.id, departure_instant_index]
                    >= x[flight_index, aircraft.id]
                )
                model.addConstr(
                    a[aircraft.id, arrival_airport.id, arrival_instant_index]
                    >= x[flight_index, aircraft.id]
                )

                for airport in problem.airports:
                    for t in range(departure_instant_index + 1, arrival_instant_index):
                        model.addConstr(
                            a[aircraft.id, airport.id, t]
                            <= 1 - x[flight_index, aircraft.id]
                        )

                model.addConstr(
                    o[aircraft.id, departure_instant_index:arrival_instant_index]
                    >= x[flight_index, aircraft.id]
                )

        """
        If a plane is not serving any flight between two consecutive instants, it can not change airports 
        """

        for aircraft in problem.aircrafts:
            for t in range(nb_instants - 1):
                for airport in problem.airports:
                    model.addConstr(
                        a[aircraft.id, airport.id, t + 1]
                        - a[aircraft.id, airport.id, t]
                        <= o[aircraft.id, t]
                    )

        """
        If a plane is not serving any flight between two consecutive instants, it cannot be occupied
        """

        for aircraft in problem.aircrafts:
            for t in range(nb_intervals):
                corresponding_flights = flights_in_interval[t]
                flight_indeces = [flight.id - 1 for flight in corresponding_flights]
                model.addConstr(
                    o[aircraft.id, t] <= x[flight_indeces, aircraft.id].sum()
                )

        """
        a plane can be in at most one airport at a given time
        """

        model.addConstr(a.sum(axis=1) <= 1)

        """
        Each plane starts at the right airport
        """

        for aircraft in problem.aircrafts:
            id, airport = aircraft.id, aircraft.starting_airport.id
            model.addConstr(a[id, airport, 0] == 1)


        model.update()
        model.optimize()

        x_solution = x.x

        assignment = self.__assignment(x_solution)

        return FlightSolution(
            assignment={
                aircraft_id: [problem.flights[flight_id - 1] for flight_id in flights]
                for aircraft_id, flights in assignment.items()
            }
        )

    def __get_instants(self, problem: FlightProblem) -> list[int]:
        departure_instants = [flight.departure_time for flight in problem.flights]
        arrival_instants = [flight.arrival_time for flight in problem.flights]
        instants = list(sorted(set(arrival_instants + departure_instants)))
        return instants
    
    def __assignment(self, solution):
        solution = solution.argmax(axis=1)

        a = {}
        for i, j in enumerate(solution):
            a.setdefault(j, []).append(i)
        return a
