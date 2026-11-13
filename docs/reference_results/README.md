# Reference results

Known-good outputs used to check that code changes do not change the results. The rule: **same inputs + same
seed ⇒ byte-identical outputs**. If a structural code change makes any file here differ, the change altered the
model's behavior, and that is a mistake unless it was intended (and then it needs a new, documented reference).

## How to check a code change

1. Make sure the inputs are the frozen ones: `python tools/check_inputs.py`, which must report "all frozen inputs match".
2. Run the model with the frozen parameter file `mtsm_data/input_parameter/mtsm_constant_configurations.csv`, i.e.
   without `--config`: `python run_examples_new_parking.py` (about 5 min). Its values are the ones listed below.
3. Compare: `python tools/compare_reference.py`. It must end with `REPRODUCED`.

`compare_reference.py` compares every file below with the file the run just wrote, byte for byte. One
exception: FleetPy writes its absolute location into `00_config.json`, so in that file FleetPy's root folder is
replaced by a placeholder before comparing.

## `lemon_grove_seed0/`

Produced on 2026-10-23 by run C of the Phase 1 verification, before the code was made self-contained.
An independent second run (D) was byte-identical. Seed 0 and `PYTHONHASHSEED=0`, in the `fleetpy` conda env
(Python 3.10.19, numpy 2.2.6, pandas 2.2.3, gurobipy 12.0.3) on Windows 10.

Run parameters (in `mtsm_constant_configurations.csv` since 2026-11-10; until then the columns of
`input_parameter.csv`, with `TRUE`, `TRUE`, `10`, `FALSE` in the removed columns `BayesianOptimization`, `TRPartA`,
`TRPartA_test_scenario_list`, `debug_mode_list`):

| test_area | transit_fare | microtransit_dist_based_rate ($/mile) | microtransit_start_fare | fleet_size | pk_fare_factor | off_pk_fare_factor | fixed2micro_factor | micro2fixed_factor | frt_headway | initial_rejection_rate | micro_rejection_penalty | random_seed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| lemon_grove | 3.615388 | 5 | 2.3811314 | 2 | 2.3703918 | 1 | 1 | 0 | 10 | 20 | 3 | 0 |

The other 40 parameters of the file have the values the code had before 2026-11-10 (`fare_scenario` 10). Other
inputs: the frozen files in `mtsm_data/` (21, with the parameter file), with checksums in `mtsm_data/MANIFEST.csv`.

| Folder | Contents | Written by the run to |
|---|---|---|
| `output/` | the 9 reported result files | `mtsm_data/lemon_grove/output/` |
| `intermediate/final_network/` | super-networks updated after the last iteration | `mtsm_data/lemon_grove/final_network/` |
| `intermediate/initial_network/` | super-networks rebuilt from the `base_*` files | `mtsm_data/lemon_grove/initial_network/` |
| `intermediate/initial_network_0719/` | copies of those, read back by the metrics code | `mtsm_data/lemon_grove/initial_network_0719/` |
| `intermediate/indiv_output/` | FleetPy user statistics of iterations 0–4 | `mtsm_data/lemon_grove/indiv_output/` |
| `intermediate/fleetpy_demand/` | demand handed to FleetPy in the last iteration | `fleetpy/data/demand/lemon_grove_example_demand/matched/lemon_grove_example_network/` |
| `intermediate/fleetpy_results/` | FleetPy results of the last iteration | `fleetpy/studies/example_study/results/example_pool_repo_AM_sc_1/` |

The intermediate files are kept so that, when something differs, the earliest differing file shows where the
change in behavior starts. Not kept, because they differ on every run: `00_simulation.log` (timestamps) and
`3-0_op-dyn_atts.csv` (computation times).

Key values (evaluation file, column `FRT_and_micro` = microtransit scenario): `tot_sub ($)` 7781.654254,
`tt_mob_lgsm_inc_with_micro` 903.047435, car mode share 0.920363, `M_trips` 68, `F_trips` 22. Column `FRT_only` = base
case: `tot_sub ($)` 2320.666326 (since 2026-11-12; before 4688.832653). Until 2026-11-12 the file had one row per
case (lines 2 and 4; the base row twice).

### Changes to this reference

- **2026-11-08, vehicle-type name** (FleetPy separation, step 3; `docs/progress.md`): the model's microtransit
  vehicle type was renamed from FleetPy's `default_vehtype` to its own `lemon_grove_vehtype` (same values, capacity
  8). The name appears in 4 FleetPy files under `intermediate/fleetpy_results/`: `00_config.json` (2 times),
  `2-0_op-stats.csv` (274), `2_vehicle_types.csv` (2), `standard_mod-0_veh_eval.csv` (2). A full run after the
  change differed from the reference only in these 4 files, and each was byte-identical to the new run after
  replacing `default_vehtype` with `lemon_grove_vehtype`. The 4 reference files were updated by that same
  replacement. All other files, including the 9 reported results, did not change.
- **2026-11-10, one parameter file** (`docs/constant_config_plan.md`): `input_parameter.csv` and the parameters in
  the code moved into `mtsm_data/input_parameter/mtsm_constant_configurations.csv`, with the same values. No
  reference file changed; each of the four steps ended with a full run that printed `REPRODUCED`.
- **2026-11-12, base case's subsidy at the base FRT headway** (`docs/open_issues.md` I-28; the first change of
  reported values): the two base rows (FRT only) of `output/lemon_grove_evaluation_zonal_partition_False.csv` now use
  the FRT cost and vehicle miles of `base_frt_headway` (20 min) instead of the run's `frt_headway` (10). A full run
  after the change differed from the reference only in this file, and there only in 13 columns of the base rows:
  `hdwy (min)` 10 -> 20, `tot_sub ($)` 4688.83 -> 2320.67, `sub_per_F_trip`, `sub_per_F_rider`, `sub_per_T_trip`,
  `sub_per_T_rider` 246.78 -> 122.14, `sub_per_F_pax_mile`, `sub_per_T_pax_mile` 241.37 -> 119.46, `sub_per_F_VMT`,
  `sub_per_T_VMT` 2.0394 -> 2.0187, `F_VMT (mi)` 2299.12 -> 1149.56, `F_PMT/F_VMT` 0.00845 -> 0.01690, `tt_VMT (mi)`
  7201.90 -> 6052.34. The microtransit row and the other 31 files did not change. The file was replaced by the new
  run's; a second full run was byte-identical (`REPRODUCED`). The old file is in git history (before this change).
- **2026-11-12, base case's accessibility on the base network** (I-28, second part, step 1): the FRT-only
  accessibility is computed on the network of `base_frt_headway` instead of the run's `frt_headway`. A full run
  differed from the reference in two places: the base rows of the evaluation file (`wghted_acc_emp_10_min` 583.20 ->
  402.64, `wghted_acc_emp_15_min` 1791.63 -> 1031.14; nothing else), and the per-zone file, which is now written as
  `output/debug_False_acc_super_network_non_micro_20.csv` (the reference's `..._non_micro_10.csv` was renamed and
  replaced). The other 30 files did not change.
- **2026-11-12, base row written once** (I-28, second part, step 2): the evaluation file had the base row twice
  (lines 2 and 3, identical); it now has 3 lines (header, base case, microtransit scenario). A full run differed from
  the reference only in this file, and it was the reference's file without line 3, byte for byte. The file was
  replaced; the final full run printed `REPRODUCED` (32 files).
- **2026-11-12, evaluation file with one line per metric** (`docs/open_issues.md` I-29): the file changed from one
  row per case (3 lines, 75 columns) to one line per metric (74 lines; columns `metric_name`, `FRT_only`,
  `FRT_and_micro`). The columns `test_scen` and `dscrptn` were removed and `microtrasnit` was corrected to
  `microtransit`. No value changed: the new file, turned back into rows, equals the old one text for text apart from
  these three points. A full run differed from the reference only in this file; it was replaced, and a second full
  run printed `REPRODUCED` (32 files).
