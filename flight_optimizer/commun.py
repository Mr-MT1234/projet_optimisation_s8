from dataclasses import dataclass
import numpy as np

@dataclass
class Airport:
    id: int
    name: str


@dataclass
class Flight:
    id: int
    departure_airport: Airport
    arrival_airport: Airport
    departure_time: int
    arrival_time: int


@dataclass
class Aircraft:
    id: int
    starting_airport: Airport