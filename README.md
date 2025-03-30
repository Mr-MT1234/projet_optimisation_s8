# Tail Assignment Problem

The **Tail Assignment Problem** involves optimizing the allocation of flights to aircraft to minimize costs. This project explores various optimization models to find optimal or near-optimal solutions for this problem.

## Setup

To set up the project, follow these steps:

-  Clone the repository:
    ```bash
    git clone https://github.com/Mr-MT1234/projet_optimisation_s8.git
    cd projet_optimisation_s8
    ```

- Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Project Structure

- `benchmarks/`: Contains the results of various benchmarks conducted throughout the project.
- `data/`: Contains the dataset used for the benchmarks, with and without maintenance constraints.
- `flight_optimizer/`: Contains the source code of this repository.
    - `commun.py`: Defines the fundamental types needed in this problem: **Airport**, **Aircraft**, and **Flight**.
    - `flight_problem.py`: Defines a representation of the **Tail Assignment Problem**, with and without maintenance constraints.
    - `graph_utils.py`: Provides utility functions for graph manipulation, used by some solvers.
    - `parsing.py`: Contains functions for parsing problem and solution files from the dataset.
    - `reporter.py`: Defines a type for visualizing and saving solutions.
    - `solution.py`: Defines a representation of a solution to the **Tail Assignment Problem**, including functionality for testing its **validity**.
    - `solvers/`: Contains all solvers developed during this project.
        - `interval_solver.py`: A solver based on **Model 1** from our report.
        - `flow_solver.py`: A solver based on **Model 2** from our report.
        - `reduced_flow_solver.py`: A solver based on **Model 3** from our report.

## Remarks

Currently, no proper error handling for syntax errors is implemented in the parsing module. Attempting to load an invalid instance or solution file may lead to a crash.


