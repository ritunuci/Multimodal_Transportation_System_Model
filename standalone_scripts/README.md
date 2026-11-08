# Standalone scripts

Scripts that the model run (`run_examples_new_parking.py`), the optimizer (`Bayesian_optimization_script.py`) and `tools/`
do not import. They were moved here from the repository root and `pre_process/` on 2026-10-23
(see `docs/progress.md`, Phase 2b), unchanged, to keep the run's code separate.

- Project scripts: plotting, equity analysis, result processing, older run and optimizer variants (`New folder/`),
  preprocessing (`pre_process/`), scratch files.
- FleetPy's own tools (`run_examples.py`, `replay_pyplot.py`, `ScenarioCreatorGUI.py`, `scenario_creator.py`) are in
  `fleetpy/` with the rest of FleetPy (since 2026-11-07).

Most of them still use absolute paths to folders outside the codebase (`D:/Ritun/Siwei_Micro_Transit/...`), so they are
not reproducible as they are. They import repo modules (`network_algorithms`, `src.*`, ...) by name, so run them from
the repository root with the root on the import path, for example `PYTHONPATH=. python standalone_scripts/plotting_code.py`.
Scripts that import FleetPy (`src.*`) also need `fleetpy/` on the import path (`PYTHONPATH=.;fleetpy` on Windows).
