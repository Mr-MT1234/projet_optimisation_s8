from abc import ABC, abstractmethod
from ..commun import *


class Solver(ABC):

    @abstractmethod
    def solve(self, problem: FlightProblem) -> FlightSolution:
        """
        Solves the flight assignement problem `problem`
        """
        ...
