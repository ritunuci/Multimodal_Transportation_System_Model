"""The multimodal transportation system model (MTSM), split out of run_examples_new_parking.py step by step
(docs/entry_script_refactor_plan.md). run_examples_new_parking.py is still the entry point; it calls
model.run_model().

- config: the run's parameters (input_parameter.csv), the startup check, and the model's fixed settings and constants.
- state: the model's state during a scenario (TravelerState, BaseCase, IterationTotals).
- trip_legs: split a traveler's path into walk / microtransit / fixed-route legs.
- paths: a traveler's networks and least generalized cost paths (car, walk + FRT, walk + microtransit + FRT).
- choice: trip costs, logit probabilities, logsum, and the mode-change threshold.
- networks: read the super-networks of an iteration.
- iteration: one iteration of the choice model for all travelers; writes the FRT and FleetPy demand files.
- microtransit: run FleetPy and update the super-networks with its results.
- results: the results of a converged scenario (costs, subsidies, accessibility, individual results, evaluation rows).
- scenarios: the study area's data (StudyArea) and the scenario loops (Scenario).
- model: run_model() (study areas, scenarios) and run_scenario() (iterate until converged, then the results).
- helpers/: the helper modules these call (network_algorithms, binary_choice, convergence_test, fleetpy_runner, ...).
"""
