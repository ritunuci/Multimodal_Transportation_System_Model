# Reference results

Known-good outputs used to check that code changes do not change the results. The rule: **same inputs + same
seed ⇒ byte-identical outputs**. If a structural code change makes any file here differ, the change altered the
model's behavior, and that is a mistake unless it was intended (and then it needs a new, documented reference).

## How to check a code change

1. Make sure the inputs are the frozen ones: `python tools/check_inputs.py`, which must report "all frozen inputs match".
2. Make sure `mtsm_data/input_parameter/input_parameter.csv` has the values listed below (including `random_seed`).
3. Run the model: `python run_examples_new_parking.py` (about 5–7 min).
4. Compare: `python tools/compare_reference.py`. It must end with `REPRODUCED`.

`compare_reference.py` compares every file below with the file the run just wrote, byte for byte. One
exception: FleetPy writes its absolute location into `00_config.json`, so in that file FleetPy's root folder is
replaced by a placeholder before comparing.

## `lemon_grove_seed0/`

Produced on 2026-10-23 by run C of the Phase 1 verification, before the code was made self-contained.
An independent second run (D) was byte-identical. Seed 0 and `PYTHONHASHSEED=0`, in the `fleetpy` conda env
(Python 3.10.19, numpy 2.2.6, pandas 2.2.3, gurobipy 12.0.3) on Windows 10.

Input parameters (`input_parameter.csv`):

| test_area | BayesianOptimization | TRPartA | TRPartA_test_scenario_list | debug_mode_list | transit_fare ($) | microtransit_dist_based_rate ($/mile) | microtransit_start_fare ($) | Fleet_size | PkFareFactor | OffPkFareFactor | Fixed2MicroFactor | Micro2FixedFactor | FRT_headway | initial_rejection_rate | micro_rejection_penalty ($) | random_seed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| lemon_grove | TRUE | TRUE | 10 | FALSE | 3.615388 | 5 | 2.3811314 | 2 | 2.3703918 | 1 | 1 | 0 | 10 | 20 | 3 | 0 |

Other inputs: the frozen files in `mtsm_data/` (21 since 2026-11-08), with checksums in `mtsm_data/MANIFEST.csv`.

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

Key values (evaluation file, row 3 = microtransit scenario): `tot_sub ($)` 7781.654254,
`tt_mob_lgsm_inc_with_micro` 903.047435, car mode share 0.920363, `M_trips` 68, `F_trips` 22.

### Changes to this reference

- **2026-11-08, vehicle-type name** (FleetPy separation, step 3; `docs/progress.md`): the model's microtransit
  vehicle type was renamed from FleetPy's `default_vehtype` to its own `lemon_grove_vehtype` (same values, capacity
  8). The name appears in 4 FleetPy files under `intermediate/fleetpy_results/`: `00_config.json` (2 times),
  `2-0_op-stats.csv` (274), `2_vehicle_types.csv` (2), `standard_mod-0_veh_eval.csv` (2). A full run after the
  change differed from the reference only in these 4 files, and each was byte-identical to the new run after
  replacing `default_vehtype` with `lemon_grove_vehtype`. The 4 reference files were updated by that same
  replacement. All other files, including the 9 reported results, did not change.
