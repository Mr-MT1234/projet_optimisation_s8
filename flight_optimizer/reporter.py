import os
from datetime import datetime
import matplotlib.pyplot as plt

from .commun import *
from .solution import FlightSolution

from itertools import repeat, chain


class Reporter:

    def plot_solution(self, solutions: list[FlightSolution], colors : list | None =None, legend=None):
        fig = plt.figure(figsize=(50, 10))
        ax = fig.subplots(1, 1)
        min_instant = float('inf')
        max_instant = float('-inf')
        max_aircraft = float('-inf')

        if colors is None:
            colors_iter = ['r', 'g', 'b', 'pink', 'puple', 'black']
        else:
            colors_iter = colors

        if legend is None:
            legend_iter = [f'solution{i}' for i in range(len(solutions))]
        else:
            legend_iter = legend


        for i, (solution, legend) in enumerate(zip(solutions, legend_iter)):
            color = colors_iter[i % len(colors_iter)]

            instants = solution.get_instants()

            min_instant = min(min(instants), min_instant)
            max_instant = max(max(instants), max_instant)
            max_aircraft = max(max(a.id for a in solution.aircrafts), max_aircraft)
            plt.plot([-1000,-1000], [1000,1000], color=color, label=legend)

            for aircraft_id, flights in solution.assignment.items():
                for flight in flights:
                    plt.plot(
                        [flight.departure_time, flight.arrival_time],
                        [aircraft_id, aircraft_id],
                        color+"-",
                        alpha=0.7
                    )
                    plt.scatter(
                        [flight.departure_time, flight.arrival_time],
                        [aircraft_id, aircraft_id],
                        color=color,
                        s=10,
                    )
                    plt.text(
                        flight.departure_time - 25,
                        aircraft_id - 0.2,
                        flight.departure_airport.name,
                        fontsize=10,
                        color=color
                    )
                    plt.text(
                        flight.arrival_time - 25,
                        aircraft_id + 0.05,
                        flight.arrival_airport.name,
                        fontsize=10,
                        color=color
                    )

        instants_plot = np.round(np.linspace(min_instant, max_instant, 50), 0)
        
        ax.legend()
        ax.set_xticks(instants_plot)
        ax.set_xticklabels(ax.get_xticks(), rotation=50)
        ax.set_xlabel("Time")
        ax.set_ylabel("Aircraft")
        ax.set_title("Aircraft schedule")
        ax.set_xlim(min_instant - 100, max_instant + 100)
        ax.set_ylim(-1, max_aircraft + 1)
        ax.set_yticks(np.arange(-1, max_aircraft + 1, 1))
        ax.grid(True)

        return fig

    def report_txt(self, solution: FlightSolution, path: str, execution_time: float | None =None):
        with open(path, 'w') as file:
            file.write("Solution:\n")
            file.write(f"cost={solution.cost}\n")
            if execution_time is not None:
                file.write(f"execution time={execution_time}s\n")
            file.write(str(solution))

