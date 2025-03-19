from abc import ABC, abstractmethod
from ..commun import *
from ..flight_problem import FlightProblem, FlightProblemMaintenance
from ..solution import FlightSolution, FlightSolutionMaintenance


class Solver(ABC):

    @abstractmethod
    def solve(self, problem: FlightProblem) -> FlightSolution:
        """
        Solves the flight assignement problem `problem`
        """

    @abstractmethod
    def solve_maintenance(self, problem: FlightProblemMaintenance) -> FlightSolutionMaintenance:
        """
        Solves the flight assignement problem with maintenance constraints `problem`
        """
