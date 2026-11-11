# Plan: one configuration file for all MTSM parameters (`mtsm_constant_configurations.csv`)

Status: **decisions made 2026-11-10 (all as recommended), plus a `description` column; steps 1 and 2 done
2026-11-10; step 3 next.** Written 2026-11-10, against commit `a28852b`; line numbers refer to that state.

## The user's request (2026-11-10)

- One config file, `mtsm_constant_configurations.csv`, with two columns: `parameter_name` and the parameter value
  (the user wrote `paramter_value`; see decision 5).
- A third column, `description` (added by the user, 2026-11-10): a very short description of the parameter, with its
  unit. No code reads it.
- The file is read into a dictionary. Each `parameter_name` gets a key, listed in a new file `mtsm_global_parameters.py`
  (the way FleetPy lists its parameter names in `src/misc/globals.py`).
- The scattered hardcoded parameters go into this file, **including the ones now in `input_parameter.csv`**.
- **Left where they are** (user's decision): the FleetPy check "expected 88 users" (`mtsm_model/microtransit.py:64`);
  the traveler coefficients (betas) and parking durations in the demand file; FleetPy's constant config and scenario
  files; the vehicle type `lemon_grove_vehtype` (capacity 8) in `mtsm_data/`.

## Feasibility

Feasible, with byte-identical results, if the four points under "What must be handled" are done. Every step ends with
a full seed-0 run: `tools/compare_reference.py` must print `REPRODUCED` (32 files).

## What goes into the file (about 55-60 parameters)

How the list was made (2026-11-10): a full seed-0 run recorded every function it calls (`REPRODUCED`); the number
literals in those functions were listed. Not counted: code under `if __name__ == "__main__":`, functions the run never
calls, unused variables, pure unit conversions (`/ 60`, `/ 3600`, `/ 100`), link-type codes (0-7), and the `999` /
`-999` placeholders for undefined ratios. FleetPy's own code (`fleetpy/`) is not included.

### 1. The columns of `mtsm_data/input_parameter/input_parameter.csv` (17)

`test_area`, `BayesianOptimization`, `TRPartA`, `TRPartA_test_scenario_list`, `debug_mode_list`, `transit_fare ($)`,
`microtransit_dist_based_rate ($/mile)` (the code divides it by `MILE_METER`; that conversion stays in the code),
`microtransit_start_fare ($)`, `Fleet_size`, `PkFareFactor`, `OffPkFareFactor`, `Fixed2MicroFactor`,
`Micro2FixedFactor`, `FRT_headway`, `initial_rejection_rate`, `micro_rejection_penalty ($)`, `random_seed`. Read by
`mtsm_model/config.py` (`read_run_config`, `RunConfig`). The four I-15 columns (`TRPartA`, `BayesianOptimization`,
`debug_mode_list`, `TRPartA_test_scenario_list`) are only checked at startup (decision 3).

### 2. The named constants in `mtsm_model/config.py` (about 22)

| Constant | Value | Meaning |
|---|---|---|
| `MILE_METER` | 1609.34 | meters per mile |
| `BASE_FRT_HEADWAY` | 20 min | FRT headway of the without-microtransit base case |
| `BASE_FRT_FARE` | $2.50 | FRT fare of the base case |
| `INDIV_CONVERG_TEST` | True | individual-level convergence test (I-16) |
| `MAXIMUM_ITERATION` | 15 | iteration limit |
| `CONVERGENCE_GAP` | 0.01 | convergence threshold |
| `MODE_CHANGE_THRESHOLD` | 0.05 | keep the previous mode if the transit probability changes by at most this |
| `AGGREGATION` | "whole_region" | how FleetPy's waiting times update the network |
| `AM_END`, `MD_END`, `PM_END` | 10 h, 15 h, 20 h (in s) | time-period boundaries |
| `PARKING_FACTOR_PEAK` / `_OFFPEAK` | 1 / 0.5 | share of the parking charge, peak / off-peak |
| `NUM_WALK_NODES`, `MICROTRANSIT_NODE_OFFSET` | 1099, 1171 | Lemon Grove node numbering |
| `F_GAS_PER_MILE` | $0.35/mile | FRT bus fuel (operator cost) |
| `M_GAS_PER_MILE` | $0.55/mile | microtransit vehicle fuel (operator cost) |
| `FARE_SCENARIO` | 10 | the fare structure; kept in output file names |
| `OPERATING_PERIODS_SCENARIOS` | [[AM, MD, PM]] | microtransit operating periods (also `OPERATING_PERIOD_1..3`) |
| `VIRTUAL_STOP_SCENARIOS` | [75] | % of nodes that are virtual stops |
| `MICROTRANSIT_RUNNING_SCENARIOS` | ["micro"] | microtransit + FRT |
| `REPOSITIONING_LIST` | [True] | FleetPy vehicle repositioning |

### 3. Values written straight into the code (about 20)

| Value | Where | Note |
|---|---|---|
| Car gas cost $0.00025/m (≈ $0.40/mile) | `helpers/network_algorithms.py:524` | the traveler's car cost in the path search |
| Time-period boundaries 10 / 15 / 20 h | `helpers/network_algorithms.py:421-425`, `helpers/update_network_files.py:139-204` | duplicates of `AM_END` etc. |
| Node ranges: walk ≤ 1098; FRT stops 1099-1170; microtransit 1171-2269 | `helpers/network_algorithms.py:493, 514` | where the FRT fare and the microtransit start fare are charged |
| Node limits ≤ 1098 (`micro`), ≤ 731 (`micro_only`) | `helpers/update_network_files.py:339, 378` | I-13 |
| Parking: half the parking duration, per started 30 min | `mtsm_model/choice.py:92-93` | |
| Rejection rate: average of the last 3 iterations from iteration 3 | `mtsm_model/model.py:91-95` | |
| Microtransit operating hours 19 / 15 / 10 from the operating periods; FRT 19 h | `mtsm_model/scenarios.py:168-175`, `helpers/testing_scenario_creation.py:22-60` | duplicated |
| FRT operating cost $170 per vehicle-hour | `mtsm_model/results.py:58, 62` | |
| Microtransit operating cost $130 per vehicle-hour | `mtsm_model/results.py:73` | |
| FRT line duration: speed 30 mph, dwell 3 min per stop, dead-end 20 min | `helpers/output_performance_metrics.py:768-771` | |
| Accessibility thresholds 5 / 10 / 15 min | `helpers/output_performance_metrics.py:372, 553` | |
| Fallback employment accessibility 431 / 5,074 / 6,341 (with microtransit), 156 / 486 / 1,020 (FRT only) | `helpers/output_performance_metrics.py:474-484, 650-660` | zones with no data and no neighbour with data |
| Meters per mile 1609, km per mile 1.609 | `helpers/output_performance_metrics.py:758, 704, 707` | disagree with `MILE_METER = 1609.34` (decision 2) |
| Default microtransit waiting time 180 s | `helpers/update_network_files.py:217, 260` | when a period has no served requests |
| FRT waiting time = half the headway | `helpers/update_initial_network.py:42-90`, `mtsm_model/results.py:247` | a rule; the factor 1/2 could be a parameter |
| Study area `"lemon_grove"` | several places | checked by name |

Also left in the code: the values `helpers/fleetpy_runner.create_config_files` writes into a missing FleetPy scenario
file (`op_max_VR_con` 3, `op_repo_horizons` 60, `op_repo_timestep` 300): they are scenario-file content.

## What must be handled for identical results

1. **Explicit types.** Values appear in output file names (`hw_10`, `fsize_2`) and in the output CSVs; an int read as
   a float (or the reverse) changes the results (`hw_10.0`, `1` instead of `1.0`). Each key in
   `mtsm_global_parameters.py` gets its type (int, float, bool, str, or a list of them), matching today's conversion
   exactly (for example `PkFareFactor` float, `Fleet_size` int). One loader converts and checks the file: every key
   present, no unknown key, every value parseable. Lists are written with `;` (`AM;MD;PM`), nested lists with `|`.
2. **Duplicates that disagree** (meters per mile 1609.34 / 1609 / 1.609): separate keys keep the results identical;
   one key changes them (decision 2).
3. **Hot loops.** The path search reads the gas cost and the node ranges per link. They are read once into local
   variables at the start of the function (a dictionary lookup per link would slow the run).
4. **Access from the helpers.** The file is read once at startup into one dictionary held in `mtsm_model/config.py`,
   which all modules import (instead of passing `cfg` into every helper function).
5. **The `description` column.** The loader requires the header `parameter_name,parameter_value,description` and
   reads only the first two columns. A description that contains a comma is quoted (the `csv` module does this when
   the file is written by code; by hand, write `"..."`). The unit goes in the description, so the keys are plain names
   (`transit_fare`, not `transit_fare ($)`). Editing a description changes the file's checksum: after a deliberate
   edit, run `tools/check_inputs.py --write` and note it in `docs/progress.md`.

## The frozen input

Facts: `input_parameter.csv` is a frozen input (`mtsm_data/MANIFEST.csv` line 2; `tools/check_inputs.py` line 19). The
optimizer (`Bayesian_optimization_script.py:255-273`) overwrites it for every candidate, writing by column position
(`rows[1][5..13]`): I-02 (it overwrites a frozen input) and I-15 (writes by position). Any version of this plan changes
how the optimizer writes its values. That is input/output, not its optimization logic, but it is a change to the
optimizer and needs the user's approval.

- **(A)** The new file is the frozen input; the optimizer edits it in place, by parameter name. Closest to today, but
  the frozen file changes during every optimization and must be restored afterwards; I-02 stays open.
- **(B) (recommended)** The new file is the frozen input and is never edited. The model takes an optional path to a
  config file (default: the frozen one). For each candidate, the optimizer copies the frozen file into its output
  folder, sets the values by parameter name, and runs the model with that copy. The reference file never changes
  (I-02 closed); each candidate's exact config is saved next to its results (the per-run provenance planned for
  Phase 3); writing by name removes the column-position problem (I-15 closed). A run with a config that differs from
  the frozen one says so at startup.

In both cases: the `input_parameter.csv` entry in `MANIFEST.csv` and `tools/check_inputs.py` is replaced by
`mtsm_constant_configurations.csv`; `input_parameter.csv` is deleted once nothing reads it (git keeps it). The
reference results in `docs/reference_results/` stay unchanged (same values); `docs/reference_results/README.md` points
to the new file.

## Steps (each ends with a full seed-0 run: `REPRODUCED`)

1. **File and keys:** `mtsm_global_parameters.py` (keys and types), `mtsm_constant_configurations.csv` with the
   reference values and a description per parameter, and the loader. A test checks that every loaded value equals
   today's value and type. Nothing uses them yet.
   *Done 2026-11-10:* 53 parameters; `config.read_constant_config()` (header, unknown, repeated and missing keys,
   values that do not convert: all listed, then stop); `tools/check_constant_config.py` compares every value and
   type with today's (`SAME: 53 parameters`; removed in step 5). The new CSV is already a frozen input (added to
   `MANIFEST.csv` and `tools/check_inputs.py`, ahead of step 4, so it is protected from the start). Not added as
   keys: the `OPERATING_PERIOD_1`/`_3` alternatives (unused), the `/ 2` rules (half the headway, half the parking
   duration), the `"lemon_grove"` name checks. Derived instead of new keys: the FRT-stop and microtransit node
   ranges (from `num_walk_nodes`, `microtransit_node_offset`) and the microtransit operating hours (sum of the
   period lengths, from `day_start_h` ... `day_end_h`: 10 / 15 / 19, checked). Full seed-0 run: `REPRODUCED`.

2. **`config.py`** switches to the dictionary. *Changed 2026-11-10:* `RunConfig` (the 13 run parameters) moved to
   step 4. Until the optimizer writes the new file, it writes its candidates into `input_parameter.csv`; a model
   that read the new file in between would run every candidate with the same frozen values, silently.
   *Done 2026-11-10:* `config.PARAMETERS = read_constant_config()` at import; the upper-case constants of
   `config.py` take their values from it (names and comments kept; `AM_END` etc. = hours x 3600). All 24 constants
   compared with the committed `config.py`: same values and types; the unused `OPERATING_PERIOD_1/2/3` removed (the
   alternatives are named in a comment). `RunConfig` unchanged (19 fields, same values and types).
   `tools/check_constant_config.py` now compares with literal copies of today's values (otherwise it would compare
   the file with itself). Full seed-0 run: `REPRODUCED`.
3. **Scattered values** replaced: `mtsm_model/` first, then the helpers.
4. **Optimizer and frozen input:** per-candidate copies written by name (B), the model takes the config path,
   `RunConfig` is built from the dictionary (moved here from step 2; the four I-15 fields and their startup checks
   go),
   `MANIFEST.csv` / `check_inputs.py` updated, `input_parameter.csv` deleted, I-02 and I-15 closed. Besides the
   reference run, one short optimizer check: one candidate, compared with what the old optimizer wrote.
5. **Docs:** README, `docs/progress.md`, `docs/reference_results/README.md`; this plan's status set to done.

## Decisions needed

1. **Frozen input:** (A) edit in place, or (B) frozen file plus per-candidate copies (needs the optimizer change)?
   *(Recommended: B.)*
2. **Meters per mile 1609.34 / 1609 / 1.609:** separate keys (identical results) or one key (results change, new
   reference needed)? *(Recommended: separate keys now, with an open item to merge them later.)*
3. **The four I-15 columns** (`TRPartA`, `BayesianOptimization`, `debug_mode_list`, `TRPartA_test_scenario_list`): drop
   them now? Once the optimizer writes by name nothing needs them. *(Recommended: drop.)*
4. **Locations:** `mtsm_constant_configurations.csv` in `mtsm_data/input_parameter/` (with the other inputs,
   checksummed); `mtsm_global_parameters.py` in `mtsm_model/` (next to `config.py`). *(Recommended: as listed.)*
5. **Second column name:** `parameter_value` (the request said `paramter_value`)? *(Recommended: `parameter_value`.)*

User's answers (2026-11-10): all five as recommended: (1) B; (2) separate keys now, open item to merge later;
(3) drop the four I-15 columns; (4) the CSV in `mtsm_data/input_parameter/`, `mtsm_global_parameters.py` in
`mtsm_model/`; (5) `parameter_value`. Also: a third column `description`, never read by code (see "What must be
handled", point 5).
