from abc import ABC, abstractmethod
from ..commun import *
from ..flight_problem import FlightProblem, FlightProblemMaintenance
from ..solution import FlightSolution, FlightSolutionMaintenance


class Solver(ABC):

    @abstractmethod
    def solve(self, problem: FlightProblem, timeout=None) -> FlightSolution:
        """
        Solves the tail assignement problem `problem`

        Args:
            - problem: the tail assignment problem to be solved
            - timeout (optional): specifies, in seconds, the maximum amount of time to be spent on the problem. 
                if no timeout is specified, no time limit is imposed

        Returns:
            If the resolution finishes before the timeout, the optimal solution is returned  
            If the resolution doesn't finish before the timeout, but a feasable solution was found, the best found solution is returned  
            If the resolution doesn't finish before the timeout, and no feasable solution were found, None is returned  
        """

    @abstractmethod
    def solve_maintenance(self, problem: FlightProblemMaintenance, timeout=None) -> FlightSolutionMaintenance:
        """
        Solves the tail assignement problem with maintenance constraints `problem`

        Args:
            - problem: the tail assignment problem to be solved
            - timeout (optional): specifies, in seconds, the maximum amount of time to be spent on the problem. 
                if no timeout is specified, no time limit is imposed

        Returns:
            If the resolution finishes before the timeout, the optimal solution is returned  
            If the resolution doesn't finish before the timeout, but a feasable solution was found, the best found solution is returned  
            If the resolution doesn't finish before the timeout, and no feasable solution were found, None is returned  
        """
