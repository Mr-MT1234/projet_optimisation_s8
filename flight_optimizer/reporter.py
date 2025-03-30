import os
import itertools
import random
import colorsys

import matplotlib.pyplot as plt
import networkx as nx

from .commun import *
from .solution import FlightSolution, FlightSolutionMaintenance
from .graph_utils import inverse_graph


class Reporter:

    def plot_solution(
        self, solutions: list[FlightSolution | FlightSolutionMaintenance], colors: list | None = None, legend=None
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
            
            # Drawing one line with each color to make sure the legend show up completely
            plt.plot([-1000, -1000], [-1000, -1000], color=color, label=legend)

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
                        flight.departure_time,
                        aircraft_id,
                        flight.departure_airport.name,
                        fontsize=10,
                        color=color,
                        verticalalignment="bottom"
                    )
                    plt.text(
                        flight.arrival_time,
                        aircraft_id,
                        flight.arrival_airport.name,
                        fontsize=10,
                        color=color,
                        verticalalignment="top",
                        horizontalalignment="right"
                    )

            if isinstance(solution, FlightSolutionMaintenance):
                for aircraft, maintenances in solution.maintenances.items():
                    for day, airport in maintenances:
                        start, end = solution.get_maintenance_interval(day)
                        plt.plot(
                            [start, end],
                            [aircraft-0.2, aircraft-0.2],
                            color="#29BF12",
                        )

                        plt.text(
                        (start+end)/2,
                        aircraft-0.2,
                        airport.name,
                        fontsize=10,
                        color="#29BF12",
                        verticalalignment="top"
                    )
                pass

        instants_plot = np.round(np.arange(0, max_instant, 24*60), 0)
        span = max_instant

        ax.legend()
        ax.set_xticks(instants_plot)
        ax.set_xticklabels(ax.get_xticks(), rotation=50)
        ax.set_xlabel("Time")
        ax.set_ylabel("Aircraft")
        ax.set_title("Aircraft schedule")
        ax.set_xlim(min_instant -0.05*span, max_instant + 0.05*span)
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

    def plot_solution_graph(self, solution: FlightSolution, aircraft_subset=None):
        if aircraft_subset is None:
            aircraft_subset = [x.id for x in solution.aircrafts]

        fig = plt.figure(figsize=(50, 10))
        ax = fig.subplots(1, 1)
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

        layers = self.__assign_layers(flight_graph)
        pos = nx.multipartite_layout(flight_graph_nx, subset_key=layers)

        nx.draw_networkx_edges(
            flight_graph_nx,
            pos,
            node_size=250,
            arrows=True,
            edge_color="gray",
            alpha=0.1,
            arrowstyle="-|>",
            arrowsize=10,
            ax=ax,
        )
        nx.draw_networkx_nodes(
            flight_graph_nx,
            pos,
            node_size=250,
            node_color="lightblue",
            alpha=0.5,
            ax=ax,
        )
        nx.draw_networkx_labels(
            flight_graph_nx,
            pos,
            font_size=12,
            ax=ax,
        )

        for aircraft in solution.aircrafts:
            if aircraft.id not in aircraft_subset:
                continue

            sorted_flights = sorted(
                solution.assignment[aircraft.id], key=lambda x: x.departure_time
            )

            sorted_flights_ids = [flight.id for flight in sorted_flights]

            path_valid = [
                (sorted_flights_ids[i], sorted_flights_ids[i + 1])
                for i in range(len(sorted_flights_ids) - 1)
                if sorted_flights_ids[i + 1] in flight_graph[sorted_flights_ids[i]]
            ]
            path_invalid = [
                (sorted_flights_ids[i], sorted_flights_ids[i + 1])
                for i in range(len(sorted_flights_ids) - 1)
                if sorted_flights_ids[i + 1] not in flight_graph[sorted_flights_ids[i]]
            ]

            color = colorsys.hsv_to_rgb(aircraft.id / len(solution.aircrafts), 0.8, 0.8)
            nx.draw_networkx_edges(
                flight_graph_nx,
                pos,
                path_valid,
                edge_color=color,
                arrowsize=40,
                ax=ax,
            )
            nx.draw_networkx_nodes(
                flight_graph_nx,
                pos,
                sorted_flights_ids,
                node_color=color,
                ax=ax,
            )
            nx.draw_networkx_edges(
                flight_graph_nx,
                pos,
                path_invalid,
                edge_color="r",
                arrowsize=60,
                ax=ax,
            )
            if sorted_flights_ids:
                ax.text(
                    *pos[sorted_flights_ids[0]],
                    s=f"$S_{{{aircraft.id}}}$",
                    color=color,
                    horizontalalignment="right",
                    verticalalignment="bottom",
                    size=20,
                )
                ax.text(
                    *pos[sorted_flights_ids[-1]],
                    s=f"$E_{{{aircraft.id}}}$",
                    color=color,
                    horizontalalignment="left",
                    verticalalignment="top",
                    size=20,
                )

        ax.set_title(f"Flight graph aircraft {aircraft}")

        return fig

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
