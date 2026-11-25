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

(`test_area` is `study_area` since 2026-11-24.) The other 40 parameters of the file have the values the code had before
2026-11-10 (`fare_scenario` 10). Since 2026-11-24 the 48 parameters are in two files with the same values: 30 in the
model file and 18 in `mtsm_data/lemon_grove/area_parameters.csv` (`docs/progress.md`, "Phase 1 step 3"); 45 (30 + 15)
since `num_walk_nodes`, `microtransit_node_offset` (derived from the files, same values) and `micro_only_max_walk_node`
(not used by the reference run) left the area file the same day. Other
inputs: the frozen files in `mtsm_data/` (21, with the parameter file; 15 since 2026-11-24), with checksums in
`mtsm_data/MANIFEST.csv` (since 2026-11-24 the parameter file there and Lemon Grove's inputs, under their new names, in
`mtsm_data/lemon_grove/MANIFEST.csv`; `docs/study_area_inputs.md` gives the old and new names).

| Folder | Contents | Written by the run to |
|---|---|---|
| `output/` | the reported result files (9; 5 since 2026-11-24) | `mtsm_data/lemon_grove/output/` |
| `intermediate/final_network/` | super-networks updated after the last iteration | `mtsm_data/lemon_grove/final_network/` |
| `intermediate/initial_network/` | super-networks rebuilt from the `base_*` files (since 2026-11-24 the templates in `mtsm_data/lemon_grove/networks/`) | `mtsm_data/lemon_grove/initial_network/` |
| ~~`intermediate/initial_network_0719/`~~ | copies of those, read back by the accessibility code; removed 2026-11-24 | ~~`mtsm_data/lemon_grove/initial_network_0719/`~~ |
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
- **2026-11-19, parking in the car's out-of-pocket cost** (`docs/progress.md`): two new parameters,
  `parking_rate_peak` and `parking_rate_offpeak` (1 $ per started interval); the car's parking cost is now part of
  its out-of-pocket cost. Three output files got new entries: the evaluation file two lines, `tt_auto_parking_cost ($)`
  and `avg_auto_parking_cost` (after `avg_auto_gas_cost`; 76 lines), and both `individual_results_*` files the column
  `parking_cost ($)` (after `out_of_pock_cost ($)`). Every parking duration in the demand file is 0, so all new values
  are 0.0 and no value changed: a full run differed from the reference only in these three files, and without the
  new lines / column each was the reference file byte for byte. The three files were replaced by the run's; the
  other 29 did not change. The parameter file (a frozen input) has the two new lines; `mtsm_data/MANIFEST.csv` was
  rewritten for it. Same day: `parking_factor_peak` (1) and `parking_factor_offpeak` (0.5) were removed and the rates
  set to 1 and 0.5 ($ per started 30 min), the same charges; no reference file changed.
- **2026-11-23, one meters-per-mile value** (`docs/open_issues.md` I-21): the FRT line lengths (1609 m per mile) and
  FleetPy's vkm and speed (1.609 km per mile) now use `meters_per_mile` (1609.34; km per mile = 1.60934); the
  parameters `meters_per_mile_frt_lines` and `km_per_mile_fleetpy` were removed. These values are used only for
  results computed after convergence, so paths, choices and FleetPy's runs did not change. A full run differed from
  the reference only in `output/lemon_grove_evaluation_zonal_partition_False.csv`, in 34 values (both columns where
  they exist): `F_VMT (mi)`, `M_VMT (mi)` and `M_avg_speed (mph)` x 0.99978873 (= 1609 / 1609.34), e.g. `F_VMT`
  2299.12 -> 2298.64 and `M_VMT` 136.863 -> 136.834; `F_oper_cost ($)` 4736.33 -> 4736.12 (FRT only 2368.17 ->
  2368.06); `M_oper_cost ($)` 3975.274 -> 3975.258; `tot_sub ($)` 7781.65 -> 7781.42 (FRT only 2320.67 -> 2320.56);
  and the subsidies per trip, rider, passenger mile and VMT, `F_PMT/F_VMT`, `M_PMT/M_VMT` and `tt_VMT (mi)` that
  depend on them (largest relative change 0.021 %). The metric names and the 76 lines stayed; the other 31 files did
  not change. The file was replaced by the run's; a second full run printed `REPRODUCED`. The parameter file (a
  frozen input) lost the two lines; `mtsm_data/MANIFEST.csv` was rewritten for it.
- **2026-11-24, accessibility calculation removed** (`docs/progress.md`, "Accessibility calculation removed"; user's
  decision, `docs/study_area_plan.md` step A): the run no longer computes the employment accessibility. The
  evaluation file lost its three lines `wghted_acc_emp_5_min`, `wghted_acc_emp_10_min`, `wghted_acc_emp_15_min`
  (76 -> 73 lines); their last values (FRT only / with microtransit) were 107.60 / 249.99, 402.64 / 4184.02 and
  1031.14 / 6331.68. They were computed on downtown San Diego's node list (`docs/open_issues.md` I-37). A full run
  differed from the reference only in this file, and it was the reference file without these three lines, byte for
  byte; the file was replaced. The run no longer writes the four per-zone files `output/debug_False_acc_super_network_*`
  or the copies in `initial_network_0719/`; these six reference files were removed (32 -> 26 files compared). Six
  frozen inputs used only by the accessibility were removed (21 -> 15; `mtsm_data/MANIFEST.csv` rewritten), and
  three parameters (`accessibility_thresholds_min`, `fallback_employment_micro`, `fallback_employment_frt`). The
  last version with the accessibility is at git tag `last-with-accessibility`. A second full run printed `REPRODUCED`.
- **2026-11-24, FRT line costs from the route table** (`docs/study_area_plan.md`, Phase 3 step 1; `docs/open_issues.md`
  I-34, item 1; `docs/progress.md`): the FRT line length and stops come from the new input
  `mtsm_data/lemon_grove/networks/frt_routes.csv` (one row per route and direction, the format of `TRA_input_data_prep`),
  and the FRT operating cost, fuel cost and vehicle miles add up its rows (before: one row per route, doubled). Lemon
  Grove's table gives each direction half of the route's link distances; the old rule (the sum of a route's distinct
  link distances) had lost a link of equal length on routes 856 (3,507.99 -> 3,701.99 m) and 916 (1,646.99 ->
  1,843.99 m); the other four routes and all stop counts are unchanged. A full run differed from the reference only in
  `output/lemon_grove_evaluation_zonal_partition_False.csv`, in 26 values (both columns): `F_VMT (mi)` 2298.64 -> 2354.03
  (FRT only 1149.32 -> 1177.02; +2.41 %), `F_oper_cost ($)` 4736.12 -> 4760.74 (2368.06 -> 2380.37; +0.52 %),
  `tot_sub ($)` 7781.42 -> 7806.04 (2320.56 -> 2332.87), and the subsidies per trip, rider, passenger mile and VMT,
  `F_PMT/F_VMT` and `tt_VMT (mi)` that depend on them. Checked: `F_VMT` and `F_oper_cost` equal, bit for bit, an
  independent calculation from the table, and `tot_sub` changed by exactly the change of `F_oper_cost`. No mode share,
  trip count, time or logsum changed; the other 25 files did not change. The file was replaced by the run's; a second
  full run printed `REPRODUCED`. The area manifest was rewritten for the new input.
- **2026-11-24, scenario travelers outside the operating periods at the scenario's headway** (`docs/open_issues.md`
  I-38, user's decision (a); `docs/progress.md`): in the scenario, travelers who depart outside the microtransit
  operating periods (here after 20:00) ride the FRT at the scenario's `frt_headway` (10 min) instead of
  `base_frt_headway` (20 min). A full run differed from the reference in 4 files: the evaluation file (34 values, all
  in `FRT_and_micro`), the scenario's individual results (121 EV travelers) and FRT ridership file, and the FRT demand
  file of FleetPy's demand folder. The base case (`FRT_only`, the `non_micro` files) and FleetPy's results did not
  change. car users 3,444 -> 3,441, transit users 298 -> 301 (3 EV travelers from car to transit), `F_trips` 22 -> 25,
  `F_revenue ($)` 65.08 -> 75.92, `tot_sub ($)` 7,806.04 -> 7,795.20 (-0.14 %), `tt_mob_lgsm_inc_with_micro` 903.05 ->
  912.09 (+1.00 %), in 34 values of the evaluation file's `FRT_and_micro` column. The 4 files were replaced by the run's; a second full run printed `REPRODUCED`.
- **2026-11-25, transfer fare rules and the exact transit search** (`docs/open_issues.md` I-22 and I-24, user's
  decisions; `docs/pathfinding_code_update.md`, section "2026-11-25"): `micro2fixed_factor` applies to the first FRT
  boarding after a microtransit ride only (before: every boarding after any microtransit link of the trip), with a
  floor, so that microtransit + FRT never cost less in fare than the FRT alone; every other FRT boarding pays the full
  fare (a re-boarding at the same walk node was free); `fixed2micro_factor` applies to the first microtransit ride
  after an FRT ride only. The transit search keeps the least-cost path per label instead of per node, so it is exact
  for these rules. A full run differed from the reference in 14 files: the evaluation file (31 values, all in
  `FRT_and_micro`), the scenario's individual results (600 rows: 597 logsum values, 2 transit users with another path
  or fare) and FRT ridership file, the MD final network, FleetPy's demand files, user statistics (iterations 0-4 and
  final), `2-0_op-stats.csv` and `standard_eval.csv`. The base case (`FRT_only`, the `non_micro` files) did not
  change. No traveler changed mode; `tot_sub ($)` 7,795.20 -> 7,796.03 (+0.01 %), `tt_mob_lgsm_inc_with_micro` 912.09
  -> 913.27 (+0.13 %), `F_revenue ($)` 75.92 -> 76.07, `M_revenue ($)` 864.88 -> 863.89, `M_trips` 68 and `F_trips`
  25 unchanged. The run was identical to the trial run of the same rules in a copy of the repository. The 14 files
  were replaced by the run's; a second full run printed `REPRODUCED`. Run time about 400 s (before about 240 s).
  Optimizer sessions before this change are not comparable for candidates with `micro2fixed_factor` < 1.
- **2026-11-25, travelers who keep their transit choice resubmit every leg** (`docs/open_issues.md` I-17, user's
  decision; `docs/progress.md`): before, only the last microtransit and the last FRT leg of a kept transit path were
  written again. A full run differed from the reference only in the FRT demand file of FleetPy's demand folder
  (`debug_False_F_transit_demand_2_op_hr_15_hw_10_virstop_75.csv`): one row more, `63287,1107,1101,11650`, the first
  of the two FRT legs of traveler 11650 (25 legs, as `F_trips`). No reported value and no FleetPy input or result
  changed. The file was replaced by the run's; a second full run printed `REPRODUCED`.
