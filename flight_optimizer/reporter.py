import os
import itertools

import matplotlib.pyplot as plt
import networkx as nx

from .commun import *
from .solution import FlightSolution
from .graph_utils import inverse_graph


class Reporter:

    def plot_solution(
        self, solutions: list[FlightSolution], colors: list | None = None, legend=None
    ):
        fig = plt.figure(figsize=(50, 10))
        ax = fig.subplots(1, 1)
        min_instant = float("inf")
        max_instant = float("-inf")
        max_aircraft = float("-inf")

        if colors is None:
            colors_iter = ["r", "g", "b", "pink", "black"]
        else:
            colors_iter = colors

        if legend is None:
            legend_iter = [f"solution{i}" for i in range(len(solutions))]
        else:
            legend_iter = legend

        for i, (solution, legend) in enumerate(zip(solutions, legend_iter)):
            color = colors_iter[i % len(colors_iter)]

            instants = solution.get_instants()

            min_instant = min(min(instants), min_instant)
            max_instant = max(max(instants), max_instant)
            max_aircraft = max(max(a.id for a in solution.aircrafts), max_aircraft)
            plt.plot([-1000, -1000], [1000, 1000], color=color, label=legend)

            for aircraft_id, flights in solution.assignment.items():
                for flight in flights:
                    plt.plot(
                        [flight.departure_time, flight.arrival_time],
                        [aircraft_id, aircraft_id],
                        color,
                        alpha=0.7,
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
                        color=color,
                    )
                    plt.text(
                        flight.arrival_time - 25,
                        aircraft_id + 0.05,
                        flight.arrival_airport.name,
                        fontsize=10,
                        color=color,
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

    def report_txt(
        self, solution: FlightSolution, path: str, execution_time: float | None = None
    ):
        with open(path, "w") as file:
            file.write("Solution:\n")
            file.write(f"cost={solution.cost}\n")
            if execution_time is not None:
                file.write(f"execution time={execution_time}s\n")
            file.write(str(solution))

    def plot_solution_graph(self, solution: FlightSolution):
        figs = [plt.figure(figsize=(50, 10)) for aircraft in solution.aircrafts]
        flight_graph_nx = nx.DiGraph()
        flight_graph = {i: [] for i in range(1, len(solution.flights) + 1)}
        for flight1, flight2 in itertools.combinations(solution.flights, 2):
            if (
                flight1.arrival_airport == flight2.departure_airport
                and flight1.arrival_time <= flight2.departure_time
            ):
                flight_graph_nx.add_edge(flight1.id, flight2.id)
                flight_graph[flight1.id].append(flight2.id)
            if (
                flight2.arrival_airport == flight1.departure_airport
                and flight2.arrival_time <= flight1.departure_time
            ):
                flight_graph_nx.add_edge(flight2.id, flight1.id)
                flight_graph[flight2.id].append(flight1.id)

        for aircraft, fig in zip(solution.aircrafts, figs):
            ax = fig.subplots(1, 1)

            layers = self.__assign_layers(flight_graph)
            pos = nx.multipartite_layout(flight_graph_nx, subset_key=layers)

            nx.draw(
                flight_graph_nx,
                pos,
                with_labels=True,
                node_size=250,
                node_color="lightblue",
                arrows=True,
                font_size=12,
                edge_color="gray",
                arrowstyle="-|>",
                arrowsize=20,
                ax=ax,
            )

            sorted_flights = sorted(
                solution.assignment[aircraft.id], key=lambda x: x.departure_time
            )

            path_valid = [
                (sorted_flights[i].id, sorted_flights[i + 1].id)
                for i in range(len(sorted_flights) - 1)
                if sorted_flights[i + 1].id in flight_graph[sorted_flights[i].id]
            ]
            path_invalid = [
                (sorted_flights[i].id, sorted_flights[i + 1].id)
                for i in range(len(sorted_flights) - 1)
                if sorted_flights[i + 1].id not in flight_graph[sorted_flights[i].id]
            ]

            nx.draw_networkx_edges(
                flight_graph_nx,
                pos,
                path_valid,
                edge_color="b",
                ax=ax,
            )
            nx.draw_networkx_edges(
                flight_graph_nx,
                pos,
                path_invalid,
                edge_color="r",
                ax=ax,
            )

            ax.set_title(f"Flight graph aircraft {aircraft}")

    def __assign_layers(self, graph: dict[int, list[int]]):
        layer_assignment = {x: 0 for x in graph}

        current_nodes = set(graph.keys()) - set(
            x for out in graph.values() for x in out
        )

        i = 0
        while current_nodes:
            for node in current_nodes:
                layer_assignment[node] = i

            current_nodes = set(x for node in current_nodes for x in graph[node])
            i += 1

        layers = {
            j: [node for node, layer in layer_assignment.items() if layer == j]
            for j in range(i)
        }

        return layers
