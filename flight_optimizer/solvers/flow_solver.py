import itertools

import gurobipy as gp

from flight_optimizer.flight_problem import FlightProblem, FlightProblemMaintenance
from flight_optimizer.solution import FlightSolution, FlightSolutionMaintenance
from .solver import Solver
from ..graph_utils import inverse_graph
from ..commun import Flight


class FlowSolver(Solver):
    def solve(self, problem: FlightProblem) -> FlightSolution:
        flight_graph = {i: [] for i in range(1, len(problem.flights) + 1)}

        for flight1, flight2 in itertools.combinations(problem.flights, 2):
            if (
                flight1.arrival_airport == flight2.departure_airport
                and flight1.arrival_time <= flight2.departure_time
            ):
                flight_graph[flight1.id].append(flight2.id)
            if (
                flight2.arrival_airport == flight1.departure_airport
                and flight2.arrival_time <= flight1.departure_time
            ):
                flight_graph[flight2.id].append(flight1.id)


        dependency_graph = {
            aircraft.id: {flight: out for flight, out in flight_graph.items()}
            for aircraft in problem.aircrafts
        }

        for aircraft in problem.aircrafts:
            dependency_graph[aircraft.id][-1] = [
                flight.id
                for flight in problem.flights
                if flight.departure_airport == aircraft.starting_airport
            ]
        dependency_graph_inv = {
            aircraft: inverse_graph(subgraph)
            for aircraft, subgraph in dependency_graph.items()
        }

        model = gp.Model()
        # model.params.OutputFlag = 0

        vars = {
            aircraft: {
                flight: [
                    model.addVar(
                        vtype=gp.GRB.BINARY, name=f"x_{aircraft}_{flight}_{flight2}"
                    )
                    for flight2 in out
                ]
                for flight, out in subgraph.items()
            }
            for aircraft, subgraph in dependency_graph.items()
        }
        variable_count = sum( len(out) for subgraph in vars.values() for out in subgraph.values() )
        print(f'number of decision variables : {variable_count}')

        # Objective
        objective = 0

        for aircraft, subgraph in dependency_graph.items():
            for flight_s, out in subgraph.items():
                for i, flight in enumerate(out):

                    objective += (
                        problem.flight_costs[flight - 1, aircraft]
                        * vars[aircraft][flight_s][i]
                    )

        model.setObjective(objective, gp.GRB.MINIMIZE)

        # Constraints
        """
        Each node must be visited by exactly one plain
        """
        for flight in problem.flights:
            constraint = 0
            for aircraft in problem.aircrafts:
                for flight_p in dependency_graph_inv[aircraft.id][flight.id]:
                    i = dependency_graph[aircraft.id][flight_p].index(flight.id)
                    constraint += vars[aircraft.id][flight_p][i]

            model.addConstr(constraint == 1)

        """
        The incoming flow to a node can not exceed the out going flow
        """
        for flight in problem.flights:
            preds = dependency_graph_inv[aircraft.id][flight.id]

            out = sum(vars[aircraft.id][flight.id])
            _in = 0

            for pred in preds:
                i = dependency_graph[aircraft.id][pred].index(flight.id)
                x = vars[aircraft.id][pred][i]
                _in += x

            model.addConstr(_in >= out)

        """
        Each plain can serve at most one flight from its initial position
        """
        for aircraft in problem.aircrafts:
            model.addConstr(sum(vars[aircraft.id][-1]) <= 1)

        model.update()
        model.optimize()

        assignment = {
            aircraft: [
                i
                for flight, out in subgraph.items()
                for i, x in zip(out, vars[aircraft][flight])
                if x.x > 0.0
            ]
            for aircraft, subgraph in dependency_graph.items()
        }

        return FlightSolution.from_assignment(assignment, problem)
    
    def solve_maintenance(self, problem: FlightProblemMaintenance):
        
        maintenance_time = problem.get_maintenance_time()
        if maintenance_time > 6:
            maintenance_time = 2
        number_of_flights = len(problem.flights)
        additional_flights = [Flight(number_of_flights + i * len(problem.airports_maintenance) + j + 1, maintenance_airport, maintenance_airport, (24*i+22)*60, (24*(i+1)+6)*60, i+1)
                for i in problem.days
                for j, maintenance_airport in enumerate(problem.airports_maintenance)
                ]
        additional_flights_ids = sorted([additional_flights[i].id for i in range(len(additional_flights))])
        
        original_flights = problem.flights[:] 
        problem.flights += additional_flights
        
        flight_graph = {i: [] for i in range(1, len(problem.flights) + 1)}

        for flight1, flight2 in itertools.combinations(problem.flights, 2):
            if (
                flight1.arrival_airport == flight2.departure_airport
                and flight1.arrival_time <= flight2.departure_time
            ):
                flight_graph[flight1.id].append(flight2.id)
            if (
                flight2.arrival_airport == flight1.departure_airport
                and flight2.arrival_time <= flight1.departure_time
            ):
                flight_graph[flight2.id].append(flight1.id)


        dependency_graph = {
            aircraft.id: {flight: out for flight, out in flight_graph.items()}
            for aircraft in problem.aircrafts
        }

        for aircraft in problem.aircrafts:
            dependency_graph[aircraft.id][-1] = [
                flight.id
                for flight in problem.flights
                if flight.departure_airport == aircraft.starting_airport
            ]
        dependency_graph_inv = {
            aircraft: inverse_graph(subgraph)
            for aircraft, subgraph in dependency_graph.items()
        }

        model = gp.Model()
        model.params.OutputFlag = 0

        vars = {
            aircraft: {
                flight: [
                    model.addVar(
                        vtype=gp.GRB.BINARY, name=f"x_{aircraft}_{flight}_{flight2}"
                    )
                    for flight2 in out
                ]
                for flight, out in subgraph.items()
            }
            for aircraft, subgraph in dependency_graph.items()
        }



        flight_maintenance=[k for k in flight_graph if problem.flights[k-1].arrival_airport in problem.airports_maintenance]
        print(flight_maintenance)

        vars_maintenance= {
            aircraft : {
                flight : model.addVar(
                    vtype=gp.GRB.BINARY, name=f"z_{flight}_{aircraft}"
                )
                for flight in flight_maintenance
            } 
            for aircraft in dependency_graph
        } 

        #for aircraft in dependency_graph:
        #    for flight in flight_maintenance:
        #        vars[aircraft][flight].append(model.addVar( vtype=gp.GRB.BINARY, name=f"z_{flight}_{aircraft}"))

                


        variable_count = sum( len(out) for subgraph in vars.values() for out in subgraph.values() )
        print(f'number of decision variables : {variable_count}')

        # Objective
        objective = 0

        for aircraft, subgraph in dependency_graph.items():
            for flight_s, out in subgraph.items():
                for i, flight in enumerate(out):
                    flight_cost = problem.flight_costs
                    maintenance_cost = problem.maintenance_costs
                    if flight in additional_flights_ids:
                        # airport_index = problem.airports_maintenance.index(problem.flights[flight-1].arrival_airport)
                        # objective += maintenance_cost[aircraft,airport_index] * vars[aircraft][flight_s][i]
                        pass
                    else:
                        objective += flight_cost[flight - 1, aircraft] * vars[aircraft][flight_s][i]

        model.setObjective(objective, gp.GRB.MINIMIZE)

        # Constraints
        """
        Each node must be visited by exactly one plain
        """
        for flight in problem.flights:
            constraint = 0
            for aircraft in problem.aircrafts:
                for flight_p in dependency_graph_inv[aircraft.id][flight.id]:
                    i = dependency_graph[aircraft.id][flight_p].index(flight.id)
                    constraint += vars[aircraft.id][flight_p][i]
            if flight.id in additional_flights_ids:
                model.addConstr(constraint <= problem.capacity_maintenance, name=f"capacity_mainenance")
            else:
                model.addConstr(constraint == 1)

        """
        The incoming flow to a node can not exceed the out going flow
        """
        for flight in problem.flights:
            for aircraft in problem.aircrafts:
                preds = dependency_graph_inv[aircraft.id][flight.id]

                out = sum(vars[aircraft.id][flight.id])
                _in = 0

                for pred in preds:
                    i = dependency_graph[aircraft.id][pred].index(flight.id)
                    x = vars[aircraft.id][pred][i]
                    _in += x

                model.addConstr(_in >= out)


        """
        Each plane can serve at most one flight from its initial position
        """
        for aircraft in problem.aircrafts:
            model.addConstr(sum(vars[aircraft.id][-1]) <= 1)
            
        """ 
        Each aircraft must be maintained at least once every problem.max_maintenance_delay days
        """
        for aircraft in problem.aircrafts:
            days = problem.days
            for i in range(1,len(days)+1,problem.max_maintenace_delay):
                window_days = days[i:i+problem.max_maintenace_delay]
                window_flights = [
                    f for f in additional_flights
                    if f.day in window_days
                ]
                constraint = 0
                for flight in window_flights:
                    for flight_p in dependency_graph_inv[aircraft.id][flight.id]:
                        idx = dependency_graph[aircraft.id][flight_p].index(flight.id)
                        constraint += vars[aircraft.id][flight_p][idx]
                model.addConstr(constraint >= 1, name=f"maintenance_{aircraft.id}_window_{i}")

        model.update()
        model.optimize()
        if model.status == gp.GRB.INFEASIBLE:
            print(model.display(), "\n\tN'A PAS DE SOLUTION!!!")
        print(model.objVal)

        assignment = {
            aircraft: [
                i
                for flight, out in subgraph.items()
                for i, x in zip(out, vars[aircraft][flight])
                if x.x > 0.0
            ]
            for aircraft, subgraph in dependency_graph.items()
        }
        maintenance = {}
        for aircraft in problem.aircrafts:
            maintenance[aircraft.id] = []
            for flight in assignment[aircraft.id]:
                if flight in additional_flights_ids:
                    maintenance_airport = problem.flights[flight-1].arrival_airport
                    day = problem.flights[flight-1].day
                    maintenance[aircraft.id].append((day, maintenance_airport))
        assignment = {aircraft: [flight for flight in flights if flight not in additional_flights_ids] 
                      for aircraft, flights in assignment.items()}
        problem.flights = original_flights

        return FlightSolutionMaintenance.from_assignment(assignment,maintenance, problem)
    