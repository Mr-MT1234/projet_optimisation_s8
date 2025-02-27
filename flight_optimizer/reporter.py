
from .commun import *
import os

import matplotlib.pyplot as plt

class Reporter:
    def __init__(self):
        ...

    def write_markdown(self, solution: FlightSolution, name: str, path: str = "./solutions"):
        with open(os.path.join(path, name), 'w'):
            pass

    
    def plot_solution(self, solution: FlightSolution):
        instants = solution.get_instants()
        
        fig = plt.figure(figsize=(50, 10))
        ax = fig.subplots(1,1)

        for aircraft_id, flights in solution.assignment.items():
            for flight in flights:
                plt.plot([flight.departure_time, flight.arrival_time], [aircraft_id, aircraft_id], 'r-')
                plt.scatter([flight.departure_time, flight.arrival_time], [aircraft_id, aircraft_id], color='b', s=10)
                plt.text(flight.departure_time, aircraft_id + 0.05, flight.departure_airport.name, fontsize=8)
                plt.text(flight.arrival_time, aircraft_id + 0.05, flight.arrival_airport.name, fontsize=8)
        
        instants_plot = np.round(np.linspace(min(instants), max(instants), 50), 0)
        ax.set_xticks(instants_plot)
        ax.set_xticklabels(ax.get_xticks(), rotation = 50)
        ax.set_xlabel('Time')
        ax.set_ylabel('Aircraft')
        ax.set_title('Aircraft schedule')
        ax.set_ylim(-1, max(a.id for a in solution.aircrafts) + 1)
        ax.set_yticks([a.id for a in solution.aircrafts])
        ax.grid(True)
        
        return fig