from abc import ABC, abstractmethod
from ..commun import *
from ..flight_problem import FlightProblem
from ..solution import FlightSolution


class Solver(ABC):

    @abstractmethod
    def solve(self, problem: FlightProblem) -> FlightSolution:
        """
        Solves the flight assignement problem `problem`
        """
        ...
