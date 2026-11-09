"""The multimodal transportation system model (MTSM), split out of run_examples_new_parking.py step by step
(docs/entry_script_refactor_plan.md). run_examples_new_parking.py is still the entry point.

- config: the run's parameters (input_parameter.csv), the startup check, and the model's fixed settings and constants.
- state: the model's state during a scenario (TravelerState, BaseCase, IterationTotals).
- trip_legs: split a traveler's path into walk / microtransit / fixed-route legs.
"""
