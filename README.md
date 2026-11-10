# Multimodal Transportation System Model (MTSM)

MTSM models a multimodal transportation system with microtransit (on-demand shared rides) integrated with
fixed-route transit (FRT), and the travelers' choice between transit and auto. For a given set of design parameters
(fleet size, FRT headway, fares, ...) it finds the equilibrium between microtransit demand and microtransit
performance, and reports the resulting mode shares, ridership, costs and accessibility. A Bayesian optimization script
searches the design parameters for the trade-off between operator subsidy and travelers' benefit.

The microtransit service is simulated with [FleetPy](https://github.com/TUM-VT/FleetPy) (TU Munich), which is
included in `fleetpy/`.

**Study area of this repository: Lemon Grove (San Diego County).** An earlier downtown San Diego configuration was
removed on 2026-11-08; the last version that has it is tagged `last-with-downtown-sd`. The one-time preprocessing in
`pre_process/` still mentions it ([`docs/open_issues.md`](docs/open_issues.md), I-14).

![MTSM framework](docs/mtsm_framework.png)

## How the model works

1. **Inputs.** Travelers (trips with origin, destination and departure time), the roadway, walk and FRT networks,
   and the design parameters: fleet size, FRT headway, FRT fare, microtransit start fare and distance-based fare,
   surge (peak) multiplier, and the microtransit-to-FRT transfer discount.
2. **Microtransit performance (FleetPy).** The microtransit trips of the current set of transit travelers are sent
   to FleetPy as requests. FleetPy simulates the fleet and returns, for each request, whether it was served and its
   wait and travel times.
3. **Transit super-network.** The microtransit performance is written into a super-network that combines walk,
   microtransit and FRT links.
4. **Multimodal least generalized cost paths.** For each traveler, the least generalized cost path is found for the
   transit mode (walk, microtransit and FRT combined) and for the auto mode.
5. **Binary logit mode choice.** Each traveler's probability of choosing composite transit or auto is computed
   from the generalized costs.
6. **Convergence.** If the choice probabilities still change between iterations, the new set of transit and auto
   travelers goes back to step 2. Otherwise the run stops and writes its results.

Fares: FRT fare per boarding; microtransit start fare plus a distance-based fare, with a peak / off-peak factor and
transfer discounts between microtransit and FRT (the former "fare scenario 10"; the columns `transit_fare ($)`,
`microtransit_start_fare ($)`, `microtransit_dist_based_rate ($/mile)`, `PkFareFactor`, `OffPkFareFactor`,
`Fixed2MicroFactor`, `Micro2FixedFactor` of `input_parameter.csv`).

## Running the model

Requirements: Windows (64-bit), conda, and a valid [Gurobi](https://www.gurobi.com) license (FleetPy uses Gurobi
for vehicle repositioning).

1. **Environment.** Create the locked conda environment as described in [`env/README.md`](env/README.md).
   Do not use `requirements.txt` or FleetPy's own install instructions; they do not match the verified environment.
2. **Check the inputs.** `python tools/check_inputs.py` must report that all frozen inputs match
   `mtsm_data/MANIFEST.csv`.
3. **Set the parameters** in `mtsm_data/input_parameter/input_parameter.csv` (design parameters, `random_seed`).
4. **Run** from the repository root, with `PYTHONHASHSEED=0` and without `PYTHONPATH`:

       python run_examples_new_parking.py

   A run takes about 5–7 minutes. Results are written to `mtsm_data/lemon_grove/output/`; the main one is
   `lemon_grove_evaluation_zonal_partition_False.csv`.
5. **Check reproducibility (optional).** With the reference parameters and seed listed in
   [`docs/reference_results/README.md`](docs/reference_results/README.md), `python tools/compare_reference.py` must
   print `REPRODUCED`: the same inputs and seed give byte-identical results.

### Bayesian optimization

`python Bayesian_optimization_script.py` runs a multi-objective Bayesian optimization (Ax/BoTorch) over fleet size,
FRT headway, FRT fare, microtransit fares, peak fare factor and transfer discount. The two objectives are total subsidy
and the increase in travelers' mobility logsum due to microtransit. For each candidate it writes the parameters into
`input_parameter.csv`, runs the model and reads the evaluation file; results go to
`mtsm_data/lemon_grove/optimization_output/`. Note: it overwrites `input_parameter.csv`, which is a frozen input
(see [`docs/open_issues.md`](docs/open_issues.md), I-02).

## Repository layout

| Path | Content |
|---|---|
| `run_examples_new_parking.py` | Entry script: fixes the hash seed, reads `input_parameter.csv`, sets the random seeds, and calls `mtsm_model.model.run_model()` |
| `mtsm_model/` | The model (see [Code map](#code-map)) |
| `Bayesian_optimization_script.py` | Bayesian optimization of the design parameters |
| `mtsm_model/helpers/` | The helper modules the model calls (see [Code map](#code-map)) |
| `get_walk_transit_skims.py`, `get_auto_skims.py` | Walk-transit and car skims; not used by a run (`docs/open_issues.md`, I-20) |
| `pre_process/` | Preprocessing of networks and demand |
| `mtsm_paths.py` | All folder locations (imported as `mtsm`) |
| `mtsm_data/` | The model's data: frozen, checksummed inputs (`MANIFEST.csv`) and the outputs of a run |
| `fleetpy/` | FleetPy, upstream version `7019960` with a few local changes listed in [`fleetpy/LOCAL_CHANGES.md`](fleetpy/LOCAL_CHANGES.md) |
| `env/` | Locked Python environment |
| `tools/` | `check_inputs.py`, `compare_reference.py`, `export_env.py` |
| `docs/` | Progress log, open issues, reference results |
| `standalone_scripts/` | Analysis and plotting scripts that the model run does not use |

## Code map

`run_examples_new_parking.py` fixes the hash seed, reads the parameters and calls `run_model()`. A run then goes
through the modules of `mtsm_model/` like this (the numbers are the steps of [How the model works](#how-the-model-works)):

```
run_examples_new_parking.py   config.read_run_config(), config.check_run_config(), random seeds
└─ model.run_model()
   └─ for each study area: scenarios.load_study_area()           folders, networks, travelers
      └─ for each scenario: scenarios.scenarios()                 headway, fleet size, ...
         └─ model.run_scenario(): until converged
            ├─ networks.read_iteration_networks()               3: the super-networks of this iteration
            ├─ iteration.run_iteration(): for each traveler
            │  ├─ paths.*                                        4: car, walk + FRT, walk + microtransit + FRT paths
            │  ├─ choice.*                                       5: costs, logit probabilities, random draw
            │  └─ trip_legs.*                                    legs of the chosen path -> FleetPy / FRT demand files
            ├─ convergence test (helpers/convergence_test.py)  6
            ├─ converged:     results.write_converged_results()  evaluation file, individual results
            └─ not converged: microtransit.run_fleetpy_and_update_networks()   2-3: FleetPy, network update
```

| Module | Content |
|---|---|
| `config.py` | `RunConfig` (the parameters in `input_parameter.csv`), the startup check, and the model's constants (iterations, convergence, gas costs, time periods, parking, scenario lists) |
| `scenarios.py` | `StudyArea` (a study area's data) and the scenario loops (`Scenario`) |
| `model.py` | `run_model()` and `run_scenario()`, the iteration loop |
| `state.py` | `TravelerState` (per-traveler values across iterations), `BaseCase` (the fixed-route-only base case), `IterationTotals` |
| `networks.py` | Reading an iteration's super-networks |
| `iteration.py` | One iteration of the choice model for all travelers |
| `paths.py` | A traveler's networks and least generalized cost paths (car and FRT paths are reused across iterations) |
| `choice.py` | Trip costs (incl. parking), logit probabilities, logsum, mode-change threshold |
| `trip_legs.py` | Splitting a path into walk, microtransit and FRT legs |
| `microtransit.py` | Running FleetPy (through `helpers/fleetpy_runner.py`) and updating the super-networks with its results |
| `results.py` | The results of a converged scenario: costs, subsidies, accessibility, individual results, evaluation rows |

The helpers these modules call are in `mtsm_model/helpers/` (moved from the repository root on 2026-11-10; imported
as `from mtsm_model.helpers import network_algorithms as n_a`, ...):

| Helper | Content |
|---|---|
| `network_algorithms.py` | Reading the super-networks and travelers; the least generalized cost path search |
| `binary_choice.py`, `convergence_test.py` | Mode choice and convergence |
| `fleetpy_runner.py` | The only module that calls FleetPy: copies MTSM's FleetPy inputs into `fleetpy/` and runs it in the same process |
| `update_network_files.py`, `get_microtransit_skims.py`, `update_initial_network.py` | Updating the super-networks with FleetPy's results; microtransit skims |
| `output_performance_metrics.py`, `testing_scenario_creation.py`, `folder_directory.py` | Output metrics, scenario and folder setup |

`mtsm_paths.py` (all folder locations) stays at the root: it derives them from its own location. How the code got
this structure, and what was checked to keep the results identical, is in
[`docs/entry_script_refactor_plan.md`](docs/entry_script_refactor_plan.md).

## Documentation

- [`docs/progress.md`](docs/progress.md): what was changed to make the model reproducible and self-contained, and
  how to continue work in a fresh clone. Read this first.
- [`docs/open_issues.md`](docs/open_issues.md): known open issues.
- [`docs/reference_results/README.md`](docs/reference_results/README.md): the reference run and how to compare with it.
- [`env/README.md`](env/README.md): the environment, and what it cannot pin (OS, CPU, Gurobi license).

## License

FleetPy is MIT-licensed (see [`fleetpy/LICENSE`](fleetpy/LICENSE)).
