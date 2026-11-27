# Open issues

Known problems and unanswered questions about the reproducible Lemon Grove model. The history of the work is in
`docs/progress.md`; this file tracks only what still needs a decision or a fix.

Paths are relative to the codebase root.

## How to use this file

- **Add an issue:** give it the next free number (`I-NN`; numbers are never reused) and add it to the index and to
  "Open". Fill in every field; write "unknown" rather than leave one out.
- **Close an issue:** set its status to `Closed (YYYY-MM-DD)`, add a **Resolution** line (what was done, the commit,
  and how it was checked, e.g. `compare_reference.py` printed `REPRODUCED`), then move the whole entry to "Closed".
  Do not delete it.
- **Status values:** `Open`, `Decision needed` (the code is clear; the user has to choose), `In progress`, `Closed`.
- **Severity:**
  - **High:** can give wrong reported results, or blocks a planned run.
  - **Medium:** a risk under conditions the reference run does not hit.
  - **Low:** documentation or housekeeping.

## Index

| ID | Title | Severity | Status | Found |
|---|---|---|---|---|
| I-01 | Gurobi license expired | High | Closed (2026-11-12) | 2026-10-23 |
| I-02 | The optimizer overwrites the frozen parameter file | Medium | Closed (2026-11-10) | 2026-10-23 |
| I-03 | The optimizer has not been run since the changes | Medium | Closed (2026-11-13) | 2026-10-23 |
| I-04 | Rows 1 and 2 of the evaluation CSV are identical | Medium | Closed (2026-11-12) | 2026-10-23 |
| I-05 | `FRT_headway = 20` overwrites a frozen network | Medium | Closed (2026-11-24) | 2026-10-23 |
| I-06 | Accessibility uses a hard-coded network for its node list | Medium | Closed (2026-11-24) | 2026-10-23 |
| I-07 | `docs/progress.md` plan table is out of date | Low | Closed (2026-11-07) | 2026-11-07 |
| I-08 | FleetPy's `README.md` still installs from `requirements.txt` | Low | Closed (2026-11-07) | 2026-10-23 |
| I-09 | The model's vehicle capacity is stored in FleetPy's vehicle file | Medium | Closed (2026-11-08) | 2026-11-07 |
| I-10 | FleetPy's example data was overwritten with downtown San Diego data | Low | Closed (2026-11-08) | 2026-11-07 |
| I-11 | Old, unused MTSM files inside `fleetpy/` | Low | Closed (2026-11-23) | 2026-11-07 |
| I-12 | FleetPy's example a) serves 90 users; its check expects 88 | Low | Closed (2026-11-23) | 2026-11-08 |
| I-13 | The `micro_only` scenario uses the downtown San Diego node limit | Low | Closed (2026-11-24) | 2026-11-08 |
| I-14 | The preprocessing code still contains downtown San Diego | Low | Closed (2026-11-26) | 2026-11-08 |
| I-15 | Unused columns in `input_parameter.csv`; the optimizer writes it by column position | Low | Closed (2026-11-10) | 2026-11-08 |
| I-16 | The aggregate convergence test is unfinished | Low | Closed (2026-11-23) | 2026-11-09 |
| I-17 | Travelers who keep their transit choice resubmit only their last microtransit and FRT leg | Medium | Closed (2026-11-25) | 2026-11-09 |
| I-18 | In later fare scenarios, every traveler gets the parking values of one traveler | Medium | Closed (2026-11-09) | 2026-11-09 |
| I-19 | The microtransit start fare always gets the FRT-to-microtransit transfer discount | Low | Closed (2026-11-25) | 2026-11-09 |
| I-20 | The skim modules and their functions in `network_algorithms.py` are not used by the run | Low | Closed (2026-11-11) | 2026-11-09 |
| I-21 | Three different meters-per-mile values (1609.34, 1609, 1.609 km) | Low | Closed (2026-11-23) | 2026-11-10 |
| I-22 | The path search can miss the least-cost path when a transfer discount applies | Medium | Closed (2026-11-25) | 2026-11-11 |
| I-23 | After a microtransit leg, the discounted FRT fare was also charged on alighting | Medium | Closed (2026-11-11) | 2026-11-11 |
| I-24 | Transfer fare rules: the discount lasts for the whole trip; re-boarding after microtransit is charged | Low | Closed (2026-11-25) | 2026-11-11 |
| I-25 | Turn on the transfer penalty (`enable_num_transfer_penalty`) with a new reference | Medium | In progress (on since 2026-11-26 on the branch `TRA_resubmission`; closes with its new reference) | 2026-11-11 |
| I-26 | A run with `--config` failed at once: the command line was handed to FleetPy | High | Closed (2026-11-11) | 2026-11-11 |
| I-27 | The optimizer crashed at its first optimization iteration (numpy/MKL in the `fleetpy` env) | High | Closed (2026-11-12) | 2026-11-12 |
| I-28 | The base case's subsidy used the FRT cost of the scenario's headway, not of the base headway | High | Closed (2026-11-12) | 2026-11-12 |
| I-29 | Evaluation file: one line per metric, read by name by the optimizer | Medium | Closed (2026-11-12) | 2026-11-12 |
| I-30 | The evaluation file holds one scenario; its base column is empty for runs without a base case | Medium | Open | 2026-11-12 |
| I-31 | The route labels of the FRT links may not show which routes run on a link | Medium | Closed (2026-11-26) | 2026-11-13 |
| I-32 | Synthetic FleetPy requests are appended out of time order; FleetPy's results depend on the order within a minute | Medium | Closed (2026-11-25) | 2026-11-16 |
| I-33 | Walking, microtransit, virtual stops and FRT stops are not kept off the freeways | Medium | Closed (2026-11-26) | 2026-11-20 |
| I-34 | Downtown San Diego and the new FRT network: the FRT code works only for Lemon Grove | High | Closed (2026-11-25) | 2026-11-23 |
| I-35 | One super-network for the whole day; MTSM is to use one per time period | High | In progress (to close on the branch `TRA_resubmission`: first run on period data) | 2026-11-23 |
| I-36 | The initial vehicle positions (`imbalanced.csv`) need a review | Medium | Open (to close on the branch `TRA_resubmission`: TRA's start file) | 2026-11-23 |
| I-37 | The Lemon Grove accessibility used downtown San Diego's node list | High | Closed (2026-11-24) | 2026-11-23 |
| I-38 | Outside the microtransit operating periods, scenario travelers ride the FRT at the base headway | High | Closed (2026-11-24) | 2026-11-24 |
| I-39 | Lemon Grove's FleetPy `crs.info` names the wrong coordinate system | Low | Closed (2026-11-26) | 2026-11-24 |
| I-40 | Output file names carry leftover parts (`zonal_partition_False`, `debug_False`, `scen_10`) | Low | Closed (2026-11-25) | 2026-11-24 |
| I-41 | FleetPy's operator settings are fixed in the code (`create_config_files`) | Low | Open | 2026-11-24 |
| I-42 | The optimizer works only on the study area of the frozen model file | Low | Closed (2026-11-26) | 2026-11-24 |
| I-43 | With FleetPy travel times per period, the operator does not replan at a switch | Medium | Closed (2026-11-26) | 2026-11-24 |
| I-44 | Fare rules to revisit on the branch: discount for the next FRT boarding only, no free re-boarding; a route change at a shared stop pays no fare; very short microtransit rides remain | Medium | Open (to revisit on the branch `TRA_resubmission`) | 2026-11-25 |
| I-45 | How the synthetic FleetPy requests are drawn (`demand_upscaling`): flattened time profile, time and direction drawn apart, repeated stop pairs | Medium | Closed (2026-11-25) | 2026-11-25 |
| I-46 | A microtransit leg's FleetPy request starts one link past the boarding stop, at the time of reaching that node | High | In progress (fixed on the branch `TRA_resubmission` 2026-11-27; closes with its new reference) | 2026-11-25 |
| I-47 | MTSM's own FleetPy demand file is in the order of the traveler list; FleetPy's results depend on the order within a time step | Medium | In progress (fixed on the branch `TRA_resubmission` 2026-11-27; closes with its new reference) | 2026-11-25 |
| I-48 | All ABM3 trip modes are in the demand file; which belong to MTSM's market is to be decided | Medium | Decision needed | 2026-11-26 |

---

## Open

### I-25: Turn on the transfer penalty (`enable_num_transfer_penalty`) with a new reference
- **Status:** In progress (turned on on the branch `TRA_resubmission` on 2026-11-26; closes with the branch's new
  reference; Open until then: reminder to turn the switch on later, user's decision 2026-11-11). **Severity:**
  Medium.
  **Found:** 2026-11-11 (checking the FRT <-> microtransit transfers).
- **What:** nothing charged a transfer: the coefficient `bt_f_trfer` of the demand file was used only on transfer
  links (type 3), which no network had. Since 2026-11-11 the path search
  (`network_algorithms.generalized_cost_dijsktra_OD_heap`) adds `bt_f_trfer` to the generalized cost per transfer
  when `enable_num_transfer_penalty` (in `mtsm_constant_configurations.csv`) is `True`: at every transit boarding
  after the first (FRT boarding walk node -> stop, microtransit boarding walk node -> micro node, when the path has
  used FRT or microtransit before) and at a route change at a shared stop (FRT link after an FRT link of another
  route). The type 3 branch was removed, and `read_super_network` stops on an unknown link type. The switch is
  `False`, so the results do not change (full seed-0 run `REPRODUCED`).
- **Impact when turned on** (checked on the reference run's final networks, AM-PM, 3,472 travelers, path search
  only): transit paths with 1 / 2 / 3 / 4 transfers 574 / 318 / 59 / 6 now and 519 / 206 / 22 / 1 with the penalty;
  each path's cost is its link costs plus `bt_f_trfer` x the transfers counted on it (all 6,944 paths, microtransit
  network and FRT-only base case). `bt_f_trfer` is 0.43-0.59 (median 0.50), about 3.3 min of FRT waiting
  (`bt_f_wt` about 0.15 per min). Most counted transfers are route changes at the four shared stops (1110, 1115,
  1119, 1160; 72 % of the AM paths that use FRT change route there, e.g. 917 -> 856 -> 936), which are free now:
  no penalty and no waiting. Full seed-0 run with the switch on (2026-11-11, through `--config`; not a reference):
  ran to the end; in the last evaluation row transit users 298 -> 291, microtransit + FRT users 6 -> 0, pure FRT
  users 15 -> 10, pure microtransit users 62 -> 66, FRT trips 22 -> 10, mode switches 51 -> 47.
- **Before turning it on:** check the route ids of the FRT links. The preprocessing kept only the first route id of
  a link served by several routes (`pre_process/process_network.py`, `construct_super_network_transit_links`:
  `route_id_str_.split(',')[0]`; route 120 became 3), so a route change in the network may be a label, not a
  transfer; the raw route file is not in the repository. Then set the switch to `True`, make and document a new
  reference in `docs/reference_results/`, together with the other changes that need one (I-19, I-21, I-22). The
  penalty depends on the path before the link, like the discounts, so the I-22 fix should cover it (state: also the
  current route).
- **Update 2026-11-13:** a full seed-0 run with the switch on (through `--config`; the frozen file and the reference
  were not changed) was compared with the reference: 21 of 32 files differ; 5 iterations as before. Evaluation file,
  base case / with microtransit: car users 3493 -> 3497 / 3444 -> 3451; transit-mode users 249 -> 245 / 298 -> 291;
  pure FRT users 19 -> 14 / 15 -> 10; FRT trips 19 -> 14 / 22 -> 10; microtransit + FRT users 6 -> 0; pure
  microtransit users 62 -> 66; `tot_sub ($)` 2320.67 -> 2333.17 / 7781.65 -> 7751.10;
  `tt_mob_lgsm_inc_with_micro` 903.05 -> 929.81 (the penalty lowers the base case more); the optimizer's objectives
  -5460.99 / 903.05 -> -5417.93 / 929.81. The same numbers as the trial of 2026-11-11. The accessibility with
  microtransit also changed (5 min: 249.99 -> 294.88); not traced (probably FleetPy's waiting times in the final
  networks, average microtransit wait 209 s -> 196 s).
- **User's decision 2026-11-13:** the switch stays `False` for now, because the route labels cannot be checked (I-31;
  the raw transit file is not at hand). Offered and not taken for now: a second switch, so that only the boardings
  after a transit leg are charged (they do not read the route label) and the route changes at a shared stop wait.
- **Update 2026-11-24:** the comparison repeated against the reference of 2026-11-24 (after the FRT route table and
  I-38): a full seed-0 run with the switch on, through `--config` (a copy of the model file; the frozen file and the
  reference unchanged; a normal run afterwards printed `REPRODUCED`). 19 of 26 files differ, 5 iterations as before.
  Evaluation file, base case / with microtransit:
  - car users 3,493 -> 3,497 / 3,441 -> 3,449; transit-mode users 249 -> 245 / 301 -> 293;
  - FRT trips 19 -> 14 / 25 -> 12; pure FRT users 19 -> 14 / 18 -> 12; microtransit + FRT users 6 -> 0; pure
    microtransit users 62 -> 66; FRT passenger miles 19.43 -> 11.01 / 30.15 -> 11.02;
  - FRT revenue 47.50 -> 35.00 / 75.92 -> 43.38; microtransit revenue 864.9 -> 926.6; `tot_sub ($)` 2,333 -> 2,345 /
    7,795 -> 7,768 (the optimizer's subsidy objective, scenario minus base, 5,462 -> 5,423);
  - `tt_mob_lgsm_inc_with_micro` 912.1 -> 935.5 (the penalty lowers the base case more); microtransit wait 209 ->
    196 s; mode switches 52 -> 48.
  - Individual results: 1,651 (scenario) and 1,282 (base case) of 3,742 rows differ, since every transit path with a
    transfer costs more; 8 (scenario) and 4 (base case) travelers change mode, all transit -> car.
  - The same direction and size as the trial of 2026-11-13. On this network most of the counted transfers are route
    changes at the four shared stops, whose labels I-31 cannot confirm.
- **User's decision 2026-11-24:** (b) the switch stays `False` on `main` (its reference unchanged) and is turned on
  on the branch `TRA_resubmission` with the new Lemon Grove inputs from `TRA_input_data_prep`, whose FRT network has
  one stop node per stop, route and direction (every route change a real transfer; I-31 does not arise there). The
  user asked to be reminded to turn it on there. It is a parameter of the model file, so both branches keep the same
  code.
- **Turned on on the branch `TRA_resubmission` (2026-11-26, user's request):** `enable_num_transfer_penalty,True` in
  `mtsm_data/input_parameter/mtsm_constant_configurations.csv` (description: False on `main`, True on the branch
  since 2026-11-26); `mtsm_data/MANIFEST.csv` rewritten (`check_inputs.py --write lemon_grove`; the area manifest
  unchanged). `main` keeps `False`.
  - A full run on the old Lemon Grove inputs (the new data is not moved in yet; 7:44): `compare_reference.py` 7
    identical, 19 differing -> `NOT REPRODUCED`, as expected. From here on `main`'s reference no longer reproduces on
    the branch; the branch gets its own reference with the new data.
  - Evaluation file against the reference (base case | scenario): F_trips 19 -> 14 | 25 -> 12; M_trips 68 -> 66;
    M+F users 6 -> 0; pure FRT users 19 -> 14 | 18 -> 12; transit users 249 -> 245 | 301 -> 293; car users
    3493 -> 3497 | 3441 -> 3449; tot_sub 2332.87 -> 2345.37 | 7796.03 -> 7768.25; `tt_mob_lgsm_inc_with_micro`
    913.27 -> 936.27; microtransit wait 209.39 -> 195.82 s; mode switches 52 -> 48. The same direction and size as
    the comparisons of 2026-11-13 and 2026-11-24 above (since then I-22, I-24, I-17, I-19 and the exact mile changed
    the reference).

### I-30: The evaluation file holds one scenario; its base column is empty for runs without a base case
- **Status:** Open. **Severity:** Medium. **Found:** 2026-11-12 (I-29).
- **What:** since I-29 the evaluation file has the columns `FRT_only` (base case) and `FRT_and_micro` (the scenario).
  Two cases do not fit:
  - *No base case:* the base case is computed only for a `micro` scenario with repositioning
    (`results.write_converged_results`). With `microtransit_running_scenarios = micro_only`, or
    `repositioning_list = False`, the column `FRT_only` stays empty, and the scenario's results are still written
    under the header `FRT_and_micro` (user's decision 2026-11-12; the line `microtransit` shows `micro_only`). The
    optimizer then stops with "the evaluation file is incomplete".
  - *More than one scenario:* the scenario lists of the parameter file (`operating_periods_scenarios`,
    `virtual_stop_scenarios`, `microtransit_running_scenarios`, `repositioning_list`) have one element each. With
    more, each converged scenario replaces the column of the one before; only the last one stays in the file
    (before I-29 each scenario added a row). There is no check at startup (user's decision: the one-element version
    stays for now).
- **To decide:** a design for runs with several scenarios (user: an architecture for this may come later), and what
  the file should show when there is no base case.

### I-35: One super-network for the whole day; MTSM is to use one per time period
- **Status:** In progress (to close on the branch `TRA_resubmission` with the first run on period data and its
  reference; status written so on 2026-11-26; since 2026-11-24: the model reads period networks; not yet run on
  period data). Open until 2026-11-24. **Severity:** High (blocks a planned run). **Found:** 2026-11-23 (planning the super-networks in
  the input-preparation repository `TRA_input_data_prep`).
- **Plan (user, 2026-11-23):** MTSM is to use one super-network per time period. `TRA_input_data_prep` builds them,
  per area and per period, with the modified `build_super_network.py` (I-33):
  - Periods: the five of SANDAG's ABM3 assignment, EA 3:00-6:00, AM 6:00-9:00, MD 9:00-15:30, PM 15:30-19:00,
    EV 19:00-3:00. The road link times per period come from ABM3's loaded link times (hwyload files).
  - What changes between periods:
    - the microtransit in-vehicle links (type 4 = the period's car time x 1.4);
    - the car network (`auto_edges`, type 7 = the period's car time).
  - What does not change: walk (0), FRT in-vehicle (1) and FRT waiting (2) are the same in every period.
    Microtransit waiting (5) starts at 180 s, as now.
  - Full grid per period and area, 24 files:
    - micro: headways 10/15/20/30/60 x virtual-stop shares 50/75/100 (15 files);
    - non_micro: the 5 headways;
    - micro_only: the 3 shares;
    - `auto_edges`.
  - Walk speed 1.6 m/s (the builder's default is 1.251).
  - Virtual stops drawn with seed 42. Every period and headway gets the same stops, and a smaller share is a subset
    of a larger one.
  - The node numbering (`num_walk_nodes`, `microtransit_node_offset`) is the same in every period.
  - File names (proposed, to agree): MTSM's current names with the period appended, e.g.
    `initial_super_network_micro_hw_10_virstop_75_AM.csv` and `auto_edges_AM.csv`.
- **What in MTSM assumes one network for all periods** (checked at `a912056`):
  1. **Periods.**
     - MTSM has four: `time_periods = ["AM", "MD", "PM", "EV"]` in `scenarios.py` and `update_network_files.py`, with
       the boundaries `config.AM_END` / `MD_END` / `PM_END`. Currently AM runs to 10:00, MD to 15:00, PM to 20:00,
       then EV.
     - ABM3 has five, with other boundaries.
     - The new demand files have requests from 3:00 (Lemon Grove: 281 in EA) and after midnight (`rq_time` past
       86,400 s).
     - To decide: switch MTSM to the five ABM3 periods, or map them.
     - Also found while checking (2026-11-23): `config.PERIOD_HOURS` takes the period lengths from `day_start_h` (5)
       and `day_end_h` (24), and `output_performance_metrics.all_scenario_micro_acc_calculation` picks its own period
       list from the microtransit operating hours (10 h: AM, PM; 15 h: AM, MD, PM; else all four). Both name the four
       periods and need the same decision.
  2. **Initial networks are keyed by variant, headway and virtual-stop share, not by period.**
     - `testing_scenario_creation.scen_create` builds the file names.
     - `paths.networks_for_traveler` uses `initial_super_network["micro"][headway][virstop][M_operating_hrs]` in
       iteration 0.
     - It uses the FRT-only network `initial_super_network["non_micro"][BASE_FRT_HEADWAY]` for every period.
  3. **The car network is one file.** `scenarios.py:108-109` reads `auto_edges.csv` once, and `paths.auto_path` and
     the micro_only fallback use it in every period.
  4. **Final networks.** `update_network_files.update_network_files` writes one final network per period, each copied
     from the same initial network (type 5 = FleetPy's waiting time for the period; type 4 x the period's detour
     ratio).
     - With period networks, each final network must start from that period's initial network.
     - Check whether the detour ratio is still wanted on top of period times. FleetPy's direct route time comes from
       its own network, which loads period times when `nw_dynamic_f` is set.
  5. **Headway update.** `update_initial_network.py` sets the headway in the Lemon Grove base networks only (Lemon
     Grove file names). It must do so in every period's file.
  6. **Related, FleetPy period times.** `TRA_input_data_prep` writes a FleetPy network folder with period subfolders
     plus `network_dynamics.csv`.
     - `fleetpy_runner.LG_STAGED_INPUTS` copies only `base/`.
     - `fleetpy/src/routing/NetworkBasic.py:249` uses `Series.iteritems()`, which pandas 2 removed.
- **Impact:** until this is done, MTSM uses one network for the whole day, so car and microtransit times do not vary
  over the day. Downtown AM link times are about 2.15 x free flow.
- **To do:**
  - a period key in the network loaders and in `networks_for_traveler`;
  - a car network per period;
  - the period definitions;
  - final networks per period from the period's initial network;
  - the headway update in every period file;
  - a new reference.
  - See also I-33 and I-34.
- **Done 2026-11-24 on `main`** (`docs/period_networks_and_car_availability_plan.md`, steps 3-5; each step
  `REPRODUCED` for Lemon Grove's whole-day inputs): the to-do list above except the new reference.
  - Periods: the area file defines them (`time_periods`, `period_start_h`, `period_end_h`, `peak_periods`), so ABM3's
    five can be set; the four names left the code (item 1).
  - The microtransit super-network (file 3) and the car network (file 5) per period, `..._<P>.csv`, with whole-day
    files as the fallback; the FRT-only networks stay whole-day (user's decision). Scenario networks and the headway
    update per period file, each period's final network from its own scenario network, the car path on the
    traveler's period (items 2-5). The file names put the period last, as proposed (`..._virstop_75_AM.csv`,
    `car_network_AM.csv`).
  - FleetPy: `network_dynamics.csv` and its folders staged, `nw_dynamic_f` set, the pandas fix (item 6).
- **Still open:** a run on period data (TRA's new Lemon Grove inputs, branch `TRA_resubmission`) and its reference;
  the detour-ratio question of item 4; FleetPy's operator does not replan at a travel-time switch (I-43, accepted
  and closed 2026-11-26).
- **2026-11-26, branch `TRA_resubmission` (user's decisions):** TRA's period networks moved in
  (`docs/new_lemon_grove_data_move.md`); the area's periods are ABM3's boundaries within a model's day of
  5:00-24:00 (`EA;AM;MD;PM;EV`, start 5, ends `6;9;15.5;19;24`; peak `AM;PM`); trips departing outside the model's
  day are not modelled (code, `config.in_model_day`; the demand file is not changed: 318 of 42,698 trips, 118
  before 5:00 and 200 after 24:00); microtransit stays `AM;MD;PM` (6:00-19:00, 13 h). FleetPy's simulation window
  is set by the run for each FleetPy run (`fleetpy_runner.simulation_window`): start at the first operating period
  (6:00), end one time step after the latest request, at least the end of the last operating period (19:00).
  `check_study_area.py`: 0 errors, 0 warnings, 1 note. Not run yet (the full run waits for the user's go-ahead).
- **The detour-ratio question of item 4, answered for period times (2026-11-26, code read):** the ratio is FleetPy's
  drive time of the served requests over their direct-route time, per period
  (`update_network_files.update_network_files`: `time_detour_ratio[P] = time_tt_drive_time[P] /
  time_tt_direct_time[P]`); with `network_dynamics.csv` both come from the same period's FleetPy times, so period
  times are not counted twice by it.
- **To decide on the branch (found 2026-11-26; user's decision to record it here): the microtransit link times are
  car time x 1.4 x the detour ratio in the final networks.**
  - In the super-networks, a microtransit in-vehicle link (type 4) has 1.4 x FleetPy's time of the same edge:
    `mtsm_data/lemon_grove/networks/super_network_micro_virstop_75.csv` against FleetPy's `base/edges.csv`
    (2,816 links), and TRA's new Lemon Grove networks per period against FleetPy's period times
    (`initial_super_network_micro_hw_10_virstop_75_AM.csv` against `21600/edges_td_att.csv`, `_MD` against
    `32400`; 2,574 links each); the 5th, 50th and 95th percentiles of the ratio are all 1.400.
  - Each final network starts from its period's initial network and multiplies its type-4 times by the period's
    detour ratio (`update_network_files.update_network_files`: `travel_time = travel_time *
    time_detour_ratio[time_period]` for `link_type == 4`), so from iteration 1 on a microtransit link costs car time
    x 1.4 x the detour ratio. In iteration 0 it is car time x 1.4.
  - If the 1.4 is a first guess of the detour, the detour is counted twice from iteration 1 on; if it stands for
    something else (e.g. microtransit slower than a car), it is not. Long-standing, so in `main`'s reference.
  - To decide: what the 1.4 stands for, and whether the final networks apply the ratio to the car time (car time x
    ratio) or, as now, to the initial microtransit time (car time x 1.4 x ratio). A change alters results, so it
    goes with the branch's new reference.

### I-36: The initial vehicle positions (`imbalanced.csv`) need a review
- **Status:** Open (to close on the branch `TRA_resubmission`, with TRA's start file; user's decision 2026-11-25,
  status written so on 2026-11-26). **Severity:** Medium. **Found:** 2026-11-23 (user: we have to look at this input file).
- **What:** FleetPy places the microtransit vehicles at the start of each simulation from
  `mtsm_data/lemon_grove/fleetpy_inputs/data/fleetctrl/initial_vehicle_distribution/lemon_grove_example_network/imbalanced.csv`,
  named by `op_init_veh_distribution,imbalanced.csv` in `lemon_grove_constant_config_ir_repo.csv` (the reference's
  `00_config.json` shows it). The file lists five road nodes, each with probability 0.2:

  | node_index | probability |
  |---|---|
  | 256 | 0.2 |
  | 400 | 0.2 |
  | 600 | 0.2 |
  | 650 | 0.2 |
  | 700 | 0.2 |

  `FleetSimulationBase` (about line 480) draws each vehicle's start node from this list with `np.random` (seed 0 in
  the reference). Without the parameter, FleetPy would spread the vehicles uniformly over the boarding nodes, or over
  all nodes if there are none.
- **What is known** (checked 2026-11-23):
  - The name comes from FleetPy's example (`fleetpy/data/fleetctrl/initial_vehicle_distribution/example_network/imbalanced.csv`:
    one node, probability 1.0, i.e. all vehicles at one place). The Lemon Grove file is not imbalanced in that sense.
  - Who chose the five nodes, and why, is not recorded. They are ordinary street nodes (car speeds 10-35 mph; none on
    a 50+ mph edge, I-33); 13 trips of the demand file start at one of them.
  - The node numbers belong to the frozen Lemon Grove road network.
- **Why it matters:**
  - With the reference's fleet of 2, each vehicle starts at one of these five nodes in every FleetPy run; the start
    positions affect the first waiting times and so the results read back by MTSM.
  - The new road networks (I-33, I-34) number the nodes anew, so the file does not carry over: a node number may not
    exist, or be another place, or be a freeway node. Downtown San Diego has no such file; FleetPy reads it from the
    network's own folder and stops if it is missing.
- **To do:**
  - decide the rule for the start positions (e.g. a few chosen nodes, all virtual stops, demand-weighted, or
    FleetPy's uniform default), and write the file per area and network (street nodes only);
  - name it after what it is, and record where the nodes come from;
  - a change belongs to a new reference.
- **2026-11-26:**
  - The file is now at `mtsm_data/lemon_grove/fleetpy/data/fleetctrl/initial_vehicle_distribution/`
    `lemon_grove_example_network/imbalanced.csv` (the folder `fleetpy_inputs/` was renamed `fleetpy/` on
    2026-11-24).
  - TRA's new Lemon Grove data has its own file (read-only check;
    `new_LG_data/lemon_grove/fleetpy_initial_vehicle_distribution/imbalanced.csv`): the same format, five nodes
    (694, 225, 863, 498, 189), 0.2 each, sum 1; all five are street nodes (`Lemon_grove_node_kind.csv`), none a
    freeway node. How they were chosen is not recorded in this repository (`TRA_input_data_prep` was not at hand).
  - User's decision: `TRA_input_data_prep` will be checked for how its `imbalanced.csv` is made, and that is
    documented. On the branch, when the data moves in: keep the five-node rule or choose another (e.g. all virtual
    stops, FleetPy's default without the parameter, or demand-weighted); a change of the rule goes with the
    branch's new reference.

### I-41: FleetPy's operator settings are fixed in the code (`create_config_files`)
- **Status:** Open. **Severity:** Low. **Found:** 2026-11-24 (Phase 3 of `docs/study_area_plan.md`). Kept in the code
  for now on the user's decision (Phase 3 decision 3), recorded here on the user's request.
- **What:** `fleetpy_runner.create_config_files` writes FleetPy's scenario file with fixed values: `op_module`
  `PoolingIRSOnly`; with repositioning `op_max_VR_con` 3, `op_repo_method` `AlonsoMoraRepositioning`,
  `op_repo_horizons` 60, `op_repo_timestep` 300; and the scenario names `example_pool_repo_AM_sc_1` /
  `example_pool_irsonly_sc_1`, by which MTSM finds FleetPy's results (`microtransit.py`,
  `update_network_files.py`, `output_performance_metrics.py`, `tools/compare_reference.py`). The area's FleetPy
  constant config (`<area>_constant_config_ir_repo.csv`) has some of them too (`op_repo_timestep` 300).
- **Impact:** none on results; changing an operator setting needs a code change, and the values are in two places.
- **Fix (later):** move them into the area's FleetPy constant config (or the model file), and read the scenario name
  from one place.
- **2026-11-26 (user's decision: take it up with I-41):** the FleetPy settings files of a study area, the vehicle type
  (`fleetpy/data/vehicles/<area>_vehtype.csv`) and the two constant configs
  (`fleetpy/studies/example_study/scenarios/<area>_constant_config_ir_repo.csv`, `..._ir.csv`), are not study-area
  data: `TRA_input_data_prep` does not write them, and a new area copies Lemon Grove's (README, "Add your own study
  area", step 3), renaming `vtype_name_full`, `network_name` and `demand_name`. Their values (capacity 8, vehicle
  costs, `op_max_wait_time` 900, `op_max_detour_time_factor` 40, `op_const_boarding_time` 30, FleetPy's fares,
  `start_time` 0, `end_time` 86400, `time_step` 60, `op_repo_timestep` 300) then come from Lemon Grove without a
  prompt to review them; e.g. an area with trips after midnight needs a later `end_time`. Kept as it is for now
  (option a); option b, to decide with this item: neutral templates in one shared place (e.g.
  `mtsm_data/input_parameter/fleetpy_templates/`) with the values to review marked.

### I-44: Fare rules to revisit on the branch: discount for the next FRT boarding only, no free re-boarding; a route change at a shared stop pays no fare; very short microtransit rides remain
- **Status:** Open (to revisit on the branch `TRA_resubmission`; user's decision 2026-11-25). **Severity:** Medium.
  **Found:** 2026-11-25 (trial of I-22 + I-24, `docs/pathfinding_code_update.md`).
- **What:** three points of the fare rules set on 2026-11-25 (I-24), in `network_algorithms.transit_label_search`:
  1. **The rules themselves:** `micro2fixed_factor` (with the floor) only for the first FRT boarding after a
     microtransit ride, `fixed2micro_factor` only for the first microtransit ride after an FRT ride, and every other
     FRT boarding pays the full fare, also a re-boarding at the same walk node right after an alighting (free before
     2026-11-25).
  2. **A route change at a shared stop node pays no fare.** Where several routes share one stop node (Lemon Grove's
     network on `main`), a path can go from an FRT link of one route to an FRT link of another at that node without
     an alighting and a boarding link, so no fare is charged: a free FRT -> FRT transfer under rule 1. On the
     reference's networks 1,227 of the 1,774 base-case paths with FRT have such a route change; many may be label
     artifacts (I-31: a shared link keeps one route's label), which is why it was left free on `main`.
  3. **Very short microtransit rides remain** (added 2026-11-25, user's request). The floor removes the fare reason
     for them (microtransit + FRT never cost less than the FRT alone), but a microtransit ride before the FRT then
     costs no extra fare as long as its fare is at most the FRT fare, so a short access ride is chosen whenever its
     ride and wait cost less than the walk it replaces. Least-cost paths on the new reference's final networks (AM-PM,
     3,472 travelers): 19 microtransit + FRT paths have a ride under 30 s (17 MD, 2 PM; 211 with the old rules and the
     exact search), no microtransit-only path. In the new reference run 7 of the 68 FleetPy requests have a direct
     ride under 30 s by FleetPy's travel times (11-28 s; 40-110 s on the super-network; the 2026-11-24 reference had
     6): travelers 4543, 6218, 4380, 5743 microtransit only (full microtransit fare, 3.24-3.96 $; not related to the
     discount), 4729, 8153, 9747 microtransit + FRT (fare at least the FRT fare). Traveler 4543's least-cost path on
     the final networks is walking; probably it kept an earlier microtransit choice (`mode_change_threshold`), not
     traced.
- **Why on the branch:** TRA's FRT network has one stop node per stop, route and direction, so every route change is
  an alighting and a re-boarding: rule 1 charges each transfer the full fare, and point 2 does not arise. With the
  transfer penalty on there (I-25), a transfer also costs `bt_f_trfer`.
- **Impact on `main`:** in the new reference (I-22); rule "no free re-boarding" changed no base-case path there.
- **To decide on the branch:** keep the full fare per FRT boarding, or a free or discounted FRT -> FRT transfer; on
  networks with shared stop nodes, whether a route change pays a fare. Very short microtransit rides: accept them, or
  set a minimum ride (distance or time) for the transfer discount, or for any microtransit request (then the search
  needs the ride length in its label); neither was tried. A rule change needs its own reference update.

---

### I-46: A microtransit leg's FleetPy request starts one link past the boarding stop, at the time of reaching that node
- **Status:** Open (to revisit and fix on the branch `TRA_resubmission`; user's decision 2026-11-26; Decision
  needed until then). **Severity:** High (FleetPy is given other requests than the travelers' paths).
  **Found:** 2026-11-25 (I-45: 21 of the 68 requests of the reference's last FleetPy file start at a node that has no
  microtransit boarding link; all 68 end at one).
- **What:** the transit paths are lists of (node reached, time at it, link type of the link into it, route), in
  `network_algorithms.transit_label_search` and before it in `getTrajectory_O_to_D`. `trip_legs.split_time_path`
  takes a microtransit leg's origin from the first element with link type 4: the node reached by the first
  microtransit link, one link past the boarding node (the microtransit node reached by the type-5 boarding link). Its
  request time is the time at that node: departure + walking + the modelled wait (type-5 link: 180 s in the initial
  networks, FleetPy's average after) + the first ride link (median 101 m, 16 s). The leg's destination is right (the
  node reached by its last type-4 link). FRT legs are built the same way (origin the next FRT stop, time after the
  FRT wait and the first link), but the FRT demand file (`debug_False_F_transit_demand_*.csv`) is only written, not
  read.
- **Impact:** FleetPy picks the rider up one link downstream, and the request enters FleetPy later than the rider
  reaches the stop, by about the modelled wait; FleetPy's own wait then counts from that time. A leg with a single
  ride link would start where it ends (none in the reference's last iteration). Long-standing (the old trajectory
  function had the same format), so in the reference.
- **To do:** the user decides the request time (the rider's arrival at the stop, or as now after the modelled wait)
  and the origin (the boarding stop); a fix changes FleetPy's inputs, so it goes with a new reference (the branch
  `TRA_resubmission`).
- **2026-11-26 (code read; user's decision: keep open, revisit and fix on the branch):**
  - Where: `trip_legs.split_time_path`, `if (pre_link_type != 4) and (link_type == 4)`: `M_origin_node = node` (the
    end of the first ride link) and `request_time = rq_time + round(time, 0)` (the time there). The boarding stop is
    `pre_node` at that element (the microtransit node reached by the waiting link, type 5); the rider's arrival at
    the stop is the time of the element before the waiting link.
  - A leg with a single ride link would start where it ends, and FleetPy declines such a request
    (`PoolingIRSOnly.user_request`: `prq.o_pos == prq.d_pos` -> rejection).
  - Possibly related, not checked: the very short FleetPy rides of I-44 (11-28 s by FleetPy's times against
    40-110 s on the super-network) lack the first ride link; the factor 1.4 of the microtransit links (I-35) also
    makes the super-network's ride longer than FleetPy's.
  - Options to decide on the branch: request time (a) the rider's arrival at the stop (recommended: FleetPy's wait
    then means what the waiting link stands for), (b) as now, after the modelled wait, (c) the departure from the
    trip origin with pickup not before the arrival at the stop (FleetPy would need an earliest pickup time; not
    checked); origin the boarding stop; FRT legs the same (their file is not read, so no result change); before
    the branch's reference run, count on `main`'s networks how many requests change origin and time. Goes with
    I-47 (the same file) in the branch's new reference.
- **2026-11-26 (first full run on the new data, fleet size 7; user's decision: leave it until this item):** 3-4
  microtransit legs per iteration from iteration 5 on (PM travelers) have a request time after the last operating
  period (19:00; last FleetPy file: 68,465-68,586 s), because the request time is after the modelled wait.
  FleetPy simulates them (the simulation window runs to one time step after the latest request, since
  2026-11-26), but `iteration.py` prints "MICRO USER OUTSIDE THE OPERATING PERIODS DETECTED" and the kept leg's
  wait (`M_wait_kept`) is EV's average (269 s in the last iteration, from those 4 requests alone) instead of PM's
  (365 s): `choice.time_period_of` of the
  request time, not of the traveler's departure. With the request time at the rider's arrival at the stop (option
  (a) above) there would be fewer such legs, not none; whether the kept leg's period should be the traveler's
  departure period is to decide with this item.
- **2026-11-27 (branch `TRA_resubmission`; user's decisions: the recommendations):** fixed in the code.
  - `trip_legs.split_time_path`: a leg's origin is its boarding stop (the node before its first in-vehicle link)
    and its request time the rider's arrival there (the time before the boarding link: microtransit the waiting
    link 5 not after a ride link 4, which would be the 0-s alighting link; FRT the link 2 not after an FRT link 1);
    a ride without such a link before it stops the run (`ValueError`; none in the networks: every microtransit
    node is entered by a link 4 or 5, every FRT stop by a link 1 or 2). FRT legs the same (their file is not read).
  - `iteration.py`: a kept leg's wait is the average of the traveler's departure period, whose network the path
    was found on (was: the period of the leg's request time); the warning checks that period too.
  - Test (2026-11-27, user's request: the 10 % sample `demand/demand_10pct.csv` as the whole demand,
    `demand_upscaling` False; `demand/demand.csv` replaced by it for the two runs and restored with `git checkout`,
    `check_inputs.py`: all inputs match): before (the code of `8d00449`) and after, fleet 7, seed 0, both 4:51-4:52.
    MTSM's choices identical (car 3,512, transit 728, microtransit trips 82, FRT trips 49, mode switches 53; base
    case unchanged). FleetPy's last demand file: origin a boarding stop 57 -> 82 of 82; the same 82 legs requested
    206 s earlier on average (median 201, 181-330 s: the modelled wait and the first ride link); rows stepping back in
    time 2 -> 0; direct rides under 30 s 2 -> 0, mean direct ride 147.7 -> 165.7 s. Scenario: microtransit VMT
    128.9 -> 137.1 mi (+6.3 %), microtransit wait 211.9 -> 217.3 s, FleetPy wait 228.9 -> 228.8 s, `tot_sub`
    15,601.6 -> 15,606.0, logsum increase 1,191.4 -> 1,187.7. The fleet is little used there (9 % utilisation), so
    the effect with all travelers can be larger; no request after 19:00 in either run. Record:
    `docs/progress.md` ("I-46 and I-47 fixed").

### I-47: MTSM's own FleetPy demand file is in the order of the traveler list; FleetPy's results depend on the order within a time step
- **Status:** Open (to do with the new reference on the branch `TRA_resubmission`; user's decision 2026-11-25).
  **Severity:** Medium. **Found:** 2026-11-16 (as part of I-32; its own item since 2026-11-25).
- **What:** `iteration.run_iteration` writes FleetPy's demand file in the order of the traveler list, not of the
  request times (the reference's last iteration: 35 of 68 rows step back in time). FleetPy rounds `rq_time` down to
  its time step (60 s) and handles the requests of one step in the order of the file (I-32), so the order of the
  traveler list decides the order within a minute, and FleetPy's results depend on it (I-32's test: a different order
  within a minute moved the share served, the waits and the vehicle miles).
- **To do:** write the file sorted by `rq_time` (a stable sort) also when `demand_upscaling` is off, as it is when on
  (`synthetic_demand.add_synthetic_requests`). It changes FleetPy's results, so it goes into the branch's new
  reference.
- **2026-11-27 (branch `TRA_resubmission`; user's decision):** fixed with I-46: `fleetpy_runner.sort_demand_file`
  (stable sort by `rq_time`, every row's text unchanged), called by `microtransit.run_fleetpy_and_update_networks`
  before FleetPy when `demand_upscaling` is off; it prints how many rows moved. Tested on the before run's last
  file (I-46's test): 4 of 82 rows moved, the same rows, sorted, a second sort moves none. In the after run the
  file was already in order (0 moved): with the requests at the stop, the 2 rows that stepped back are gone.

### I-48: All ABM3 trip modes are in the demand file; which belong to MTSM's market is to be decided
- **Status:** Decision needed (user's decision 2026-11-26: keep all modes for now, decide later). **Severity:**
  Medium. **Found:** 2026-11-26 (moving TRA's new Lemon Grove inputs in, held decision 3).
- **What:** TRA's demand file (`mtsm_data/lemon_grove/demand/demand.csv` on the branch `TRA_resubmission`, 42,698
  trips) has every ABM3 trip of the area, with its ABM3 mode in the column `trip_mode` (not read by the run): car
  29,727 (`DRIVEALONE` 16,035, `SHARED2` 7,747, `SHARED3` 5,945), `WALK` 12,270, `BIKE` 234, `EBIKE` 35, `TAXI` 227,
  `TNC_SINGLE` 60, `SCH_BUS` 8, transit 137 (`WALK_LOC` 99, `WALK_PRM` 30, `KNR_PRM` 6, `PNR_PRM` 2). MTSM chooses again
  between car and transit (walk, FRT, microtransit; a walk-only path counts as transit) for every trip; 1,328
  travelers have no car (`auto_available` False) and ride transit or walk.
- **Impact:** the size of the market and so the mode shares, the transit and microtransit trips, the subsidy per
  rider and the logsum. Old Lemon Grove's 3,742 trips came from the old preprocessing (`generate_demand_files.py`);
  which ABM modes it kept was not checked.
- **Options:** (a) keep all; (b) leave out walking and biking trips (`WALK`, `BIKE`, `EBIKE`); (c) also school bus,
  taxi and ride-hailing; (d) other. A filter would be in the code (as the model's day, 2026-11-26), not in the
  demand file. Goes with the branch's new reference.

## Closed

### I-39: Lemon Grove's FleetPy `crs.info` names the wrong coordinate system
- **Status:** Closed (2026-11-26); until then: Open (to close on the branch `TRA_resubmission`, where `crs.info` is updated; user's decision
  2026-11-26). **Severity:** Low. **Found:** 2026-11-24 (writing the input specification).
- **What:** `mtsm_data/lemon_grove/fleetpy_inputs/data/networks/lemon_grove_example_network/base/crs.info` says
  `EPSG:32632` (WGS 84 / UTM zone 32N, in Germany). The node coordinates in `nodes.csv` (`pos_x` about 6.27-6.33
  million, `pos_y` about 1.82-1.86 million) look like NAD83 California zone 6 in US feet (`EPSG:2230`). Probably a
  leftover of FleetPy's example data, like I-10.
- **Impact:** none on results. FleetPy reads the file on startup (`NetworkBasic.py:173`) and uses it only to convert
  coordinates to longitude/latitude for its real-time plot (`FleetSimulationBase._start_realtime_plot` and the
  plot update), which the run does not turn on. Wrong for anyone who plots or exports the coordinates.
- **Fix (later; user's decision 2026-11-24):** confirm the system (e.g. one node against a map), correct the file,
  rewrite `mtsm_data/MANIFEST.csv`, full run must print `REPRODUCED`.
- **2026-11-26 (user's decision): `crs.info` is updated on the branch `TRA_resubmission`; `main` keeps
  `EPSG:32632`.**
  - The file is now at `mtsm_data/lemon_grove/fleetpy/data/networks/lemon_grove_example_network/base/crs.info`
    (the folder `fleetpy_inputs/` was renamed `fleetpy/` on 2026-11-24); it still says `EPSG:32632`.
  - TRA's new FleetPy network (`new_LG_data/lemon_grove/fleetpy_network/base/crs.info`, read-only check) already
    says `EPSG:2230`, the system named above, so moving the new data in corrects it.
- **Resolution (2026-11-26, branch `TRA_resubmission`):** TRA's FleetPy network moved in;
  `fleetpy/data/networks/lemon_grove_example_network/base/crs.info` says `EPSG:2230`;
  `mtsm_data/lemon_grove/MANIFEST.csv` rewritten. No effect on results (FleetPy uses the file only for its
  real-time plot). `main` keeps `EPSG:32632`.

### I-33: Walking, microtransit, virtual stops and FRT stops are not kept off the freeways
- **Status:** Closed (2026-11-26); until then: In progress (to close on the branch `TRA_resubmission`, once TRA's networks are in use; status
  written so on 2026-11-26; since 2026-11-23: decided; the builder change and the networks built with it are not in
  MTSM yet). **Severity:** Medium. **Found:** 2026-11-20 (user: the walk mode needs to stay off the freeways).
  Title until 2026-11-23: "Walking, virtual stops and FRT stops are not kept off the freeways".
- **What:** the walk links (type 0) are a copy of every road edge (`pre_process/build_super_network.py`, `build`:
  `add(a, b, dist, dist / walk_speed, WALK)` for each edge; it rebuilds the frozen networks with the same links, so
  the old notebook did the same).
  Nothing removes the freeways, so a walk path can run along a freeway or its ramps. In the same way the virtual
  stops (microtransit boarding, `virtual_stops`: drawn from all walk nodes or read from a file) and the walk node an
  FRT stop is joined to (`nearest_walk_nodes`: the nearest of all walk nodes) can be a node on a freeway.
- **User's requirement 2026-11-20:** a future road network will mark which links are freeways. With it, no one
  walks on a freeway link, and neither the virtual stops nor the FRT stops are at freeway nodes.
- **What the frozen inputs show** (checked 2026-11-20 with a read-only script in the session scratchpad):
  - The road network (FleetPy's `edges.csv`, 2,816 edges) has no road type, only distance and car travel time. The
    car speed is the only clue: 90 edges at 60 mph (22.2 km) and 14 at 50 mph (4.5 km); the next speed down is
    45 mph (28 edges). 102 edges (26.3 km) are at 50 mph or more.
  - All 102 are walk links in the super-networks (e.g. `base_super_network_lemon_grove_micro_hw_10_virstop_75.csv`:
    2,808 walk links = the 2,816 edges less 8 duplicate pairs).
  - 62 nodes lie on these edges; 52 of them also lie on slower roads (where a walker can get on and off). No trip
    starts or ends at one of the other 10, and no FRT stop is joined to any of the 62. 83 trip starts and 74 trip
    ends (of 3,742) are at nodes that touch a fast edge.
  - Virtual stops: each microtransit super-network (`base_...micro_hw_10_virstop_75.csv` and the 16
    `initial_super_network_micro_hw_*_virstop_75.csv`) has the same 815; 48 are at nodes that touch a fast edge, 8 of
    them at nodes that lie only on fast edges (a rider set down there can leave only along the freeway).
  - `edges_all_infos.geojson` in the same folder has a `road_type` column, but it is not the Lemon Grove network:
    11,366 features in EPSG:32632 with German stop names; none matches an edge of `edges.csv`. It looks like a
    leftover of FleetPy's example data (see I-10).
- **Impact:** not known. The outputs do not show which walk links the reference's paths use (the ridership files
  have FRT links only), so it was not checked whether any traveler walks on these edges. If one does, the walk time
  and the transit generalized cost of that traveler are too low (a freeway is a short, direct line), and so is the
  transit share. The same walk links are in the accessibility networks (accessibility removed 2026-11-24). A microtransit ride to or from one of the 8
  virtual stops above ends where only a freeway walk leads on.
- **To do as written 2026-11-20** (superseded by the decisions of 2026-11-23 below; microtransit now also stays off
  the freeways, and the ramp-end nodes are decided):
  - `build_super_network.py` reads the freeway mark from the road edges (e.g. a column `is_freeway`, 0/1).
  - No walk link for a freeway edge. The car links and the microtransit links (the vehicles) keep them.
  - A freeway node: a node whose links are all freeway links (it has no walk link left). It is never a virtual stop
    (left out of the share draw; a virtual stop file that names one stops the run with an error) and never the walk
    node of an FRT stop (the nearest walk node that is not a freeway node).
  - To decide: nodes where a freeway link meets a street (ramp ends; 52 in the frozen network if the fast edges are
    the freeways, 40 of them virtual stops). They keep their street walk links; whether they may be virtual stops or
    FRT stop nodes is open.
  - Also check: no trip of the demand file starts or ends at a freeway node (`pre_process/generate_demand_files.py`,
    `map_mgra_to_nodes`, maps the zones to nodes), the walk network stays connected, and every trip end and stop can be reached on foot.
  - Changes the networks and so the results: belongs to a new reference. Until the new network exists, the car
    speed (e.g. 50 mph or more) is the only way to find the freeways in the frozen inputs.
- **The new road networks (2026-11-23):** the road, FRT and demand inputs of Lemon Grove and downtown San Diego are
  being rebuilt in the input-preparation repository `TRA_input_data_prep` (MGRA15 zones, SANDAG ABM3). Every edge is
  marked in `<prefix>_edge_kind.csv`: `link_kind` is `street`, `alley` or `driveway` (from SANDAG's Bike_Net), or
  `freeway`, `fwy_connector` or `ramp` (from SANDAG's TNED network). Freeway and ramp edges are one-way. Every node
  is marked in `<prefix>_node_kind.csv`: `kind` is `street` or `freeway`.
- **Decisions (user, 2026-11-23):**
  - Freeways, freeway-to-freeway connectors and ramps are **car only**: only the car network (`auto_edges.csv`, link
    type 7) uses them.
  - **Walking (type 0) and microtransit (type 4) do not use them** (new: the To do of 2026-11-20 kept the
    microtransit links on the freeways). Both use only the street, alley and driveway edges, which are all two-way.
  - FleetPy's microtransit network is rebuilt without the freeway edges as well, so that FleetPy and the
    super-network agree. All nodes are kept, so the node numbers do not change.
  - Virtual stops are drawn from **all street nodes** (any node with a street, alley or driveway edge), never from
    freeway nodes. This settles the "To decide" of 2026-11-20: street nodes where a ramp ends keep their walk links
    and may be virtual stops and FRT stop nodes.
    - For reference: the old code drew virtual stops from all road nodes, demand node or not. The frozen Lemon Grove
      75 % networks have 815 virtual stops among the 1,099 walk nodes; 593 of them are demand nodes
      (`is_demand_node` in `pre_nodes.csv`). 70 % of the trip ends in the demand file are at a virtual stop.
  - FRT stops are joined only to street nodes. The FRT files written in `TRA_input_data_prep` already give each stop
    the coordinates of its street node.
  - Freeway nodes stay in every layer, to keep the numbering (walk node i = microtransit node offset + i = FleetPy
    node i). They have no walk or microtransit links and no boarding.
  - How:
    - `pre_process/build_super_network.py` gets an optional input, e.g. `--local-edges FILE`
      (`from_node,to_node`): the edges that get walk and microtransit links.
    - Virtual stops and FRT stop joins are only at nodes on these edges. Car links are on every edge.
    - Without the option the builder behaves as now, so the frozen networks still reproduce.
    - The change is written in `TRA_input_data_prep`, which keeps a copy of the builder identical to MTSM `008c6ac`,
      and is then copied back into MTSM's `pre_process/`.
- **Checked in `TRA_input_data_prep` (2026-11-23):** the street, alley and driveway edges form one connected two-way
  network that reaches every street node.
  - Lemon Grove: 2,574 of 2,601 edges; 1,047 street nodes + 20 freeway nodes.
  - Downtown: 2,154 of 2,255 edges; 730 street nodes + 70 freeway nodes.
- **Found 2026-11-24** (Phase 7 of `docs/study_area_plan.md`, reading `TRA_input_data_prep`'s README for the
  README section "Add your own study area"): the networks built with freeways do not run in MTSM yet. Their freeway
  nodes keep their numbers but have no microtransit link (type 4), and `config.derive_node_numbering` requires the
  type-4 nodes to be exactly `M..M+N-1` (and takes `M` as the smallest of them); the run stops at startup. Taking in
  the new networks therefore also means relaxing that rule (type-4 nodes a subset of `M..M+N-1`, `M` found another
  way) and the checker's node rules with it. Until then the README tells users of `TRA_input_data_prep` to build the
  streets-only network (`--no-freeways`). Not run: no `TRA_input_data_prep` outputs are in this repository.
- **Done 2026-11-24** (`docs/period_networks_and_car_availability_plan.md`, step 1; user confirmed the layout from
  `TRA_input_data_prep`'s `build_super_network.py`: walk node n -> microtransit node offset + n, freeway nodes keep
  their numbers in both layers without links): `derive_node_numbering` takes `M` from the waiting links (type 5),
  allows unused twins in `M..M+N-1`, and requires the type-4 nodes to be the twins of the walk links' nodes; the
  checker also requires the vehicle start nodes to have a road edge. Tested on TRA's new Lemon Grove network (the
  user's untracked `new_LG_data/`: N = 1,067, M = 1,189) and on four broken copies (all stopped); Lemon Grove's
  numbering unchanged (1,099, 1,171). The README's `--no-freeways` advice is replaced.
- **2026-11-24 (user's request): the new builder is in MTSM's `pre_process/`.** `pre_process/build_super_network.py`
  is `TRA_input_data_prep`'s copy at its commit `b68886b` (2026-11-24, "Super-networks per ABM3 period; freeways car
  only ..."), content identical, line endings CRLF as in this repository. The only change against the old copy is the
  option `--local-edges` (walk and microtransit links only on the local edges; virtual stops and FRT stop joins only
  at their nodes; the car network keeps every edge). Checked on a small made-up network (3 x 3 street grid, a
  freeway node, 4 stops, 2 routes): without the option all three variants and the car network come out byte for
  byte as the old script writes them; with it the freeway edges have no walk or microtransit link, the freeway node
  no link at all, the car network is unchanged, and the stop nearest the freeway node is joined to a street node.
  The user's decision: I-33 closes on the branch `TRA_resubmission`, once TRA's networks built with it are in use.
- **Closes when** the new builder is in MTSM's `pre_process/` and the networks built with it are in use (a new
  reference; see I-34 and I-35).
  - **2026-11-26:** the builder condition no longer applies: `pre_process/` is to be removed on the branch (I-14,
    user's decision 2026-11-25; the inputs are prepared in `TRA_input_data_prep`). I-33 closes on the branch
    `TRA_resubmission` once TRA's networks are in use there (with its new reference).
- **Checked 2026-11-26 on TRA's new Lemon Grove data** (read-only; the user's untracked `new_LG_data/lemon_grove/`,
  `network/Lemon_grove_edge_kind.csv` and `_node_kind.csv`): all 115 super-networks in `super_network/`
  (`initial_super_network_*.csv`, every variant, headway, share and period) have no walk (type 0) or microtransit
  (type 4) link on any of the 27 car-only edges (15 `ramp`, 11 `freeway`, 1 `fwy_connector`), and no virtual stop
  (type 5) or FRT stop join (types 2 and 3) at any of the 20 freeway nodes; the car network (`auto_edges_AM.csv`,
  2,601 edges) has all 27.
- **Resolution (2026-11-26, branch `TRA_resubmission`):** TRA's networks, built with car-only freeways, connectors
  and ramps, are the branch's inputs since 2026-11-26 (`docs/new_lemon_grove_data_move.md`; the check of 2026-11-26
  above covers the five period files and the FRT-only files now in `networks/`); `tools/check_study_area.py` on
  the moved data: 0 errors, 0 warnings. `main` keeps its old networks (walk links on the fast roads) as its
  record.

### I-31: The route labels of the FRT links may not show which routes run on a link
- **Status:** Closed (2026-11-26); until then: Open (to close on the branch `TRA_resubmission`, once TRA's networks are in use: its FRT network has
  one stop node per stop, route and direction, so every route change is an alighting and a boarding; user's
  decision 2026-11-25, status written so on 2026-11-26). **Severity:** Medium. **Found:** 2026-11-13 (before turning on the transfer penalty, I-25).
- **What:** every FRT link (type 1) of the super-networks has one route number. In the raw Lemon Grove transit file
  a link served by several routes had a list (e.g. `[856, 936]`); the old preprocessing kept only the first number
  (`pre_process/process_network.py`, `construct_super_network_transit_links`: `route_id_str_.split(',')[0]`; route
  120 became 3). The raw file is not in the repository, and the user does not have it at hand (2026-11-13), so the
  links that had a list cannot be found.
- **What the frozen network shows** (`initial_super_network_non_micro_hw_20.csv`, 130 FRT links, routes 4, 520, 856,
  916, 917, 936):
  - Routes 916, 917 and 936 each end at a stop in the middle of route 856: 917 at stop 1115, 936 at stops 1119 and
    1110 (the same walk node), 916 at stop 1160. These are the only stops served by more than one route. This is
    what the first-number rule gives if these routes in fact run on along 856's street (856 is the smallest number,
    so every shared link would be labelled 856); it is also what three routes that really end on 856 look like. The
    network alone cannot tell.
  - Routes 4, 520, 856 and 936 are each in two pieces without a link between them. For 856 and 936 the pieces have
    the same length and lie on each other (most stops of one piece are at the walk node of a stop of the other), so
    they are probably the two directions (stops on the two sides of the street); for 4 and 520 they lie less close.
    Not a label problem. Every FRT link exists in both directions.
- **Impact:** none on the reference: nothing reads the route label for a cost while `enable_num_transfer_penalty` is
  `False`. With the switch on, a route change at a shared stop costs `bt_f_trfer`; if a label is only the first of a
  list, a rider who stays on the same bus is charged a transfer (e.g. 917 -> 856 -> 936: two penalties, about 1.0, or
  about 6.6 min of FRT waiting). 72 % of the AM paths that use FRT change route at the four shared stops (I-25), so
  the labels decide most of the penalty's effect. If the labels are right, the opposite gap is there: a transfer at
  a shared stop has no waiting time.
- **To do:** when the raw transit and road network files are available and the super-network is rebuilt (user,
  2026-11-13: possibly later), keep all routes of a link. `pre_process/build_super_network.py` takes one route number
  per link, so it needs a way to carry several (and the path search a rule for "same bus"). Then decide I-25.
  Other ways to check the labels: the operator's route maps.
- **Also noticed, not checked further:** the distances of the FRT links look too short. For every route the sum of
  its link distances is less than the straight line between its two end stops (walk-node coordinates in feet; e.g.
  route 856: 1,836 against about 2,875 m; route 4: 1,205 against about 1,995 m); multiplied by 1.609 they fit. They
  may be miles x 1,000, not metres. How the model uses this column (FRT passenger miles, the per-mile subsidy
  values) was not checked. See also I-21.
  - **2026-11-26 (read-only check):** in TRA's new Lemon Grove data (`new_LG_data/lemon_grove/frt/frt_edges.csv`,
    110 FRT edges) `distance` is in metres: it equals the milepost difference x 1609.344 (median ratio 1.0000), and
    its median ratio to the straight line between the two stops is 1.00. A comparison of the route lengths
    (`networks/frt_routes.csv` against TRA's `frt_routes.csv`) does not settle the old network: route 4 2,618
    against 2,669 m, but 856, 916 and 936 are 1.7-1.8 times longer in TRA's data, with other stop counts (856: 19
    against 14 and 15), so the routes probably do not cover the same stretch. User's decision: the old network's
    distances stay as they are (main keeps it as the record); the question does not carry over to the branch.
- **Resolution (2026-11-26, branch `TRA_resubmission`):** TRA's networks are the branch's inputs since 2026-11-26
  (`docs/new_lemon_grove_data_move.md`). Checked on them: `networks/frt_links.csv` has 122 stop nodes, none used by
  two routes, and one route label per link, so every route change is an alighting and a boarding and the question
  of this item does not arise there. `main`'s old network keeps it (labels, and the unresolved FRT distances) as
  its record.

### I-14: The preprocessing code still contains downtown San Diego
- **Status:** Closed (2026-11-26); until then: Open (to close on the branch `TRA_resubmission`, where `pre_process/` is removed; user's decision
  2026-11-25; status written so on 2026-11-26). **Severity:** Low. **Found:** 2026-11-08 (removing downtown San Diego, step 2b).
- **What:** `pre_process/process_network.py` (`get_transit_link_route`, `construct_initial_network`, `__main__`
  with `new_downtown_sd=True`) and the `__main__` of `pre_process/generate_demand_files.py`
  (`test_area = ["downtown_sd","lemon_grove"]`) still build or handle both study areas.
- **Why it was left:** this is the one-time preprocessing that built the frozen inputs in `mtsm_data/`; the run
  does not use it, and it cannot be run here (its source data is not in the repository), so an edit could not be
  tested. The user decided to keep it unchanged as the record of how the inputs were made (2026-11-08).
- **Impact:** none on results. The repository is not yet free of downtown San Diego code.
- **Fix (later):** remove `"downtown_sd"` from the loops and delete the downtown branches and the downtown part of
  `__main__`, with a note that the preprocessing has not been re-run since; the original stays at tag
  `last-with-downtown-sd`. Alternatively, bring the source data into the repository first, so that the
  preprocessing can be re-run and checked.
- **2026-11-23 (user's request; the downtown parts are not changed):** `synthesize_requests_with_trend_time` and its
  helper `make_time_sampler` (the "Ritun added" block, the only part of `pre_process/` the run imported) moved
  unchanged to `mtsm_model/helpers/synthetic_demand.py`; `mtsm_model/microtransit.py` imports it from there (still as
  `syn_rq`, call still commented out). `generate_demand_files.py` lost the block and its two imports used only by it
  (`colorama`, `typing`). The run now loads nothing from `pre_process/` (checked: no `pre_process` module in
  `sys.modules` after importing the entry script; `pyproj` is no longer loaded by the run either).
  - Checked: the moved lines are byte-identical to the old ones; old and new function give byte-identical output
    files on the reference's FleetPy demand file (seed 42, 204 new requests; defaults, ordered, undirected, independent
    marginals). Full run: `compare_reference.py` printed `REPRODUCED` (32 identical).
  - User's choice: `standalone_scripts/` is left untouched, so the four scripts in `standalone_scripts/New folder/`
    that import the function from `pre_process.generate_demand_files` (`run_examples_new.py`,
    `run_examples_new_LG_rejection.py`, `run_examples_new_TRC_R1.py`, `run_examples_new_parking_old.py`) now fail at
    that import.
  - I-14 stays open for the downtown parts (the user will take up downtown San Diego with I-34).
  - 2026-11-25 (user's decision): `standalone_scripts/` removed from the repository (27 files, in the git history;
    the last commit that has them is the parent of the removal commit), including the four scripts above.
- **2026-11-25 (user's decision):** `pre_process/` is out of date: the inputs are now prepared in the repository
  `TRA_input_data_prep` (https://github.com/ritunuci/TRA_input_data_prep). On the branch `TRA_resubmission` the folder
  is to be removed and the README to say that the data is prepared there; that closes I-14 on the branch. On `main`
  the folder stays as the record of how the old Lemon Grove inputs were made.
- **Resolution (2026-11-26, branch `TRA_resubmission`; user's decisions 2026-11-25 and 2026-11-26):** `pre_process/`
  removed on the branch (its four files `build_super_network.py`, `dictionary_initialization.py`,
  `generate_demand_files.py`, `process_network.py`); the inputs are prepared in `TRA_input_data_prep`, which
  `README.md` now says ("Data", and "Building the inputs with TRA_input_data_prep"; the layout table lost the
  folder). The remaining mentions got "(removed on the branch 2026-11-26)": code comments in
  `network_algorithms.py`, `synthetic_demand.py`, `update_initial_network.py`; `docs/study_area_plan.md`,
  `docs/entry_script_refactor_plan.md`; `docs/study_area_inputs.md` now names `TRA_input_data_prep` for the demand
  file. Checked: no module imports from `pre_process` (none since 2026-11-23). `main` keeps the folder with its
  downtown parts, as the record of how the old Lemon Grove inputs were made. No run (the full run waits for the
  user's go-ahead).

### I-43: With FleetPy travel times per period, the operator does not replan at a switch
- **Status:** Closed (2026-11-26). **Severity:** Medium (affects runs with `network_dynamics.csv`, e.g. the new
  Lemon Grove data on the branch `TRA_resubmission`; not the reference). **Found:** 2026-11-24
  (`docs/period_networks_and_car_availability_plan.md`, step 5, test with MD travel times x 2).
- **What:** when FleetPy loads a period's travel times (`NetworkBasic.update_network`), it calls the operator's
  `inform_network_travel_time_update`. The operator MTSM uses, `PoolingIRSOnly` (`PoolingInsertionHeuristicOnly`),
  does not implement it (`FleetControlBase` only logs "inform_network_travel_time_update not implemented for this
  operator", once per switch in `00_simulation.log`). The routing engine has the new times, so later offers and
  insertions use them, but the plans of vehicles already assigned are not recomputed at the switch.
- **Impact:** unknown; near a switch, offers and vehicle plans can mix the old and the new period's times. The
  pooling operators with batch optimization (`RidePoolingBatchOptimizationFleetControlBase`) do implement it.
- **Fix (later):** check how FleetPy upstream handles it for `PoolingIRSOnly`, or implement the update (recompute the
  current plans at the switch) as a local FleetPy change; or accept and document it.
- **Checked (2026-11-26):** what FleetPy does with `network_dynamics.csv` (code read; MTSM's settings:
  `NetworkBasicWithStore`, `time_step` 60, `start_time` 0):
  1. **Loading:** at every time step FleetPy calls `NetworkBasic.update_network(sim_time)`; at a time listed in
     `network_dynamics.csv` it loads that folder's `edges_td_att.csv` (folder `0` at the first step). A listed time
     that is not a multiple of `time_step`, or lies before `start_time`, is never loaded, without a message. The
     times of TRA's new Lemon Grove data (`new_LG_data/`: 0, 10800, 21600, 32400, 55800, 68400) are all hit.
  2. **Planning:** offers and insertions use the current edge times; `NetworkBasicWithStore` empties its stored
     route times at every load (`_reset_internal_attributes_after_travel_time_update`).
  3. **Moving:** `move_along_route` reads each edge's current time at every step, so a vehicle on the road drives at
     the new period's times from the switch on.
  4. **What remains:** a trip planned before a switch keeps its node route, the shortest under the old times
     (`FleetSimulationBase.update_vehicle_routes` is never called); its planned stop times and promised pickup times
     are recomputed only at its next stop (`VehiclePlan.update_plan`), and a plan that turns late is kept. Upstream
     FleetPy (TUM-VT/FleetPy, `main`, checked 2026-11-26) is the same: `PoolingIRSOnly` does not implement
     `inform_network_travel_time_update`.
- **Resolution:** accepted as is (user's decision 2026-11-26). FleetPy uses each period's travel times for loading,
  planning and moving, as intended; the remaining effect (the route choice of trips underway at a switch) is
  accepted. No code change. Offered, not taken: a `tools/check_study_area.py` error for a switch time that is not a
  multiple of FleetPy's `time_step`. Docs only; no run.

### I-42: The optimizer works only on the study area of the frozen model file
- **Status:** Closed (2026-11-26); Open until then. **Severity:** Low. **Found:** 2026-11-24 (Phase 7 of `docs/study_area_plan.md`, writing the README
  section "Add your own study area"). Recorded on the user's decision (Phase 7 decision 6): documented now, fixed later.
- **What:** `Bayesian_optimization_script.py` takes the study area from the frozen model file
  (`STUDY_AREA = config.PARAMETERS[gp.G_STUDY_AREA]`) and writes each candidate's parameter file as a copy of the
  frozen file (`config.FROZEN_CONSTANT_CONFIG_FILE`), so a candidate's `study_area` is always the frozen file's
  (`lemon_grove`). Its output folder name is fixed: `folder_name = "LG_submission_results_R2"`, inside
  `mtsm_data/<area>/optimization_output/`.
- **Impact:** none on results. To optimize another area, a user sets `study_area` in the frozen model file and rewrites
  the manifests (README, "Add your own study area"); Lemon Grove then no longer reproduces the reference until the
  value is set back. Another area's results go to a folder named `LG_submission_results_R2`.
- **Fix (later):** an optimizer option `--config <file>`: the base file of the candidates' copies (and so the study
  area); the output folder named after the area or by an option. A code change: full run `REPRODUCED` and a short
  optimizer run.
- **Resolution (2026-11-26, user's decisions: the folder `Bayesian_optimization_output/BO_results_<area>`, its place
  left to me; the optimizer adapts to the area it runs on; an earlier run's results are never overwritten; on main):**
  - `python Bayesian_optimization_script.py [--config <file>]`: the base file of the candidates, as for the model
    (without it, the frozen model file). The script puts it into `MTSM_CONFIG_FILE` before `config` is imported, so
    `study_area`, the area file, the operating periods and the virtual-stop share are the base file's; each
    candidate's file is a copy of the base file with its seven values (`write_candidate_config`). Neither file is
    changed. A missing `--config` file or area file stops it at once.
  - Results: `mtsm_data/Bayesian_optimization_output/BO_results_<area>/` (`mtsm_paths.optimization_results_dir`;
    `mtsm_data/` holds everything a run writes, and the name carries the area, so the folder is outside the area's).
    Same contents as before, plus `base_config.csv` (the base file at the start); `run_log.txt` starts with the base
    file, the area and the folder. If the folder has any file, the optimizer stops at once and says to move or rename
    it (e.g. `BO_results_lemon_grove_<date>`); the next run writes a new one.
  - Removed: `AreaPaths.optimization_output_dir` and `mtsm_data/lemon_grove/optimization_output/` (empty but for
    `.gitkeep`); `.gitignore` ignores `mtsm_data/Bayesian_optimization_output/` instead. The search space, `N_BATCH`,
    the objectives and the rest of the optimizer are unchanged.
  - Checked: a full run printed **`REPRODUCED`** (26 files) and `check_inputs.py` passed; a base copy with
    `study_area` `no_such_area` stopped with "the study area's parameter file is missing" and a missing `--config`
    file with "no such file", neither writing anything; a short optimizer run without `--config`
    (stopped by hand during the 7th candidate; 6 candidates of about 6.5 min each): `run_log.txt` names the frozen file
    and `lemon_grove`, `base_config.csv` equals the frozen file, each candidate copy differs from it only in the seven
    values (candidate 4 in six: its fleet size 2 is the frozen value), `per_call_results.csv` has the 6 rows; a second
    start then stopped at once with the move-or-rename message, the folder untouched. The `[WinError 32]` lines about
    FleetPy's `00_simulation.log` in the model's output are not new (4 in the reproduced full run too). The test
    folder was moved out of the repository.

### I-40: Output file names carry leftover parts (`zonal_partition_False`, `debug_False`, `scen_10`)
- **Status:** Closed (2026-11-25); Open until then. **Severity:** Low. **Found:** 2026-11-24 (Phase 1 of `docs/study_area_plan.md`). Kept on the
  user's request (decision 4 of Phase 1: keep the names for now).
- **What:** names written by the run still contain parts of removed options:
  - `zonal_partition_False`: the evaluation file `<area>_evaluation_zonal_partition_False.csv` (`scenarios.py`);
  - `debug_False`: the FRT ridership files `debug_False_<area>_..._transit_edges_rders_scen_10.csv`
    (`output_performance_metrics.write_fixed_transit_link_vmt`), FleetPy's demand file
    `<area>_debug_False_fleetpy_demand.csv` (`scenarios.py`, `fleetpy_runner.create_config_files` and the FleetPy
    scenario files) and the FRT demand file `debug_False_F_transit_demand_...` (`scenarios.py`);
  - `scen_10` (the only fare scenario, `fare_scenario`): the individual-results and ridership files (`results.py`,
    `output_performance_metrics.py`).
  - The optimizer reads two of these names, partly with fixed values: `lemon_grove_evaluation_zonal_partition_False.csv`
    and `individual_results_micro_M_fsize_<d>_op_hr_15_hw_<f>_virstop_75_scen_10.csv`
    (`Bayesian_optimization_script.model_output_files`; `op_hr_15` and `virstop_75` fixed).
- **Impact:** none on results; the names are longer than needed and carry meaningless parts.
- **Fix (later):** drop the parts in the run and the optimizer together (and the optimizer's fixed `op_hr_15`,
  `virstop_75`); a reference update that renames files only (and the FleetPy demand name inside FleetPy's
  outputs); `fare_scenario` can then leave the parameter file.
- **Resolution (2026-11-25, user's decision "do it now"):** the leftover parts are dropped, in the run and the
  optimizer together; the names are made in one place, `mtsm_paths` (`evaluation_file`, `individual_results_file`,
  `frt_ridership_file`, `fleetpy_demand_name`, `frt_demand_file`):

  | Before | Since 2026-11-25 |
  |---|---|
  | `<area>_evaluation_zonal_partition_False.csv` | `<area>_evaluation.csv` |
  | `individual_results_<setup>_M_fsize_<f>_op_hr_<h>_hw_<hw>_virstop_<v>_scen_10.csv` | `individual_results_<setup>_M_fsize_<f>_op_hr_<h>_hw_<hw>_virstop_<v>.csv` |
  | `debug_False_<area>_<setup>_<f>_op_hr_<h>_hw_<hw>_virstop_<v>_transit_edges_rders_scen_10.csv` | `<area>_<setup>_<f>_op_hr_<h>_hw_<hw>_virstop_<v>_transit_edges_rders.csv` |
  | `<area>_debug_False_fleetpy_demand.csv` (FleetPy's demand, also in its scenario file and `00_config.json`) | `<area>_fleetpy_demand.csv` |
  | `debug_False_F_transit_demand_<f>_op_hr_<h>_hw_<hw>_virstop_<v>.csv` | `F_transit_demand_<f>_op_hr_<h>_hw_<hw>_virstop_<v>.csv` |

  The optimizer's `model_output_files` takes them from `mtsm_paths`, with the operating hours and the virtual-stop
  share of the parameters (one value each, else it stops) instead of the fixed `op_hr_15` and `virstop_75`. The
  parameter `fare_scenario` is gone (`config.FARE_SCENARIO` and its check, `results.py`'s `test_scenario`, the
  "Testing Scenario" print); a parameter file that still has it stops with a message saying to delete the line
  (`mtsm_global_parameters.REMOVED_PARAMETERS`). Reference: the 7 files renamed (`git mv`, contents unchanged) and
  in `intermediate/fleetpy_results/00_config.json` the `rq_file` line; a full run then printed **`REPRODUCED`** (26
  files). Files with the old names from earlier runs are still in `mtsm_data/lemon_grove/output/` and FleetPy's
  demand folder (git-ignored outputs, among them the optimizer runs of 2026-11-12/13); not deleted.

### I-32: Synthetic FleetPy requests are appended out of time order; FleetPy's results depend on the order within a minute
- **Status:** Closed (2026-11-25); In progress and Open until then. **Severity:** Medium. **Found:** 2026-11-16 (user's question).
- **What:** `synthesize_requests_with_trend_time` (`pre_process/generate_demand_files.py`; since 2026-11-23 in
  `mtsm_model/helpers/synthetic_demand.py`, unchanged, I-14) writes the new requests
  after the old ones (`pd.concat([df, new_df])`), not merged in time order. The new block is not in time order
  either: the times come from the random sampler in the order they are drawn. The only caller is the commented-out
  "Ritun added" block in `mtsm_model/microtransit.py`. That block adds 3 x the microtransit users of the iteration as
  synthetic local requests to FleetPy's demand file before FleetPy runs.
- **How FleetPy reads the file** (`fleetpy/src/demand/demand.py`, `load_demand_file` and `get_new_travelers`): it
  rounds `rq_time` down to the time step (60 s in the Lemon Grove config) and groups the rows by it; the groups are
  sorted by time. So every request enters the simulation at its own minute, wherever its row is. Within one minute
  the requests keep the file order, and `ImmediateDecisionsSimulation.step` handles them one after the other (each
  is inserted into the vehicle plans before the next one is looked at). So only the order within a minute matters.
- **Checked 2026-11-16** (scripts in the session scratchpad; nothing in the repo changed; FleetPy demand files and
  result folders made for the check under their own names and removed afterwards):
  - The FleetPy demand file of the last iteration of the reference run (68 requests) is not in time order itself
    (35 rows step back in time; MTSM writes it in the order of the agent list). FleetPy handles this already.
  - The commented-out call, repeated on a copy of that file: 204 new rows, 272 in all. A second file held the same
    rows sorted by `rq_time` (stable sort). Loaded with FleetPy's own `Demand.load_demand_file`, every request enters
    at the same minute in both files; the order differs in 29 of the 49 minutes that hold more than one request
    (23 minutes hold an old and a new request).
  - FleetPy runs with the reference's config (repositioning, fleet 2, seed 0). The 68-request file gives the
    reference's `standard_eval.csv` byte-identical (check of the method). Appended against sorted:

    | | appended | sorted |
    |---|---|---|
    | users served (of 272) | 234 | 238 |
    | waiting time, mean / median (s) | 498.2 / 526.1 | 490.1 / 490.0 |
    | waiting time, 90 % quantile (s) | 858.3 | 846.4 |
    | the 68 MTSM users: served / mean wait (s) | 61 / 564.7 | 58 / 516.7 |
    | shared rides | 17.5 % | 15.1 % |
    | total vkm | 735.0 | 738.9 |

    The first difference is at 07:02: two new requests in the same minute, the later one (by second) first in the
    appended file. From there the two runs go apart.
- **Impact:** none on the reference (the call is commented out). If the block is switched on, the share served and
  the waiting times that MTSM reads back from FleetPy (`modal split rq` for the rejection rate, the waiting times in
  the final networks) depend on the row order within a minute. This is not a wrong entry time; it is FleetPy's
  sensitivity to the order of requests in the same minute, and any change of that order moves the results like this
  (one different insertion changes the vehicle plans for all later requests).
- **To do (when the block is switched on):** sort the combined rows by `rq_time` (stable) before writing, so the
  order is the order of the request times and does not depend on how the rows were made. Sorting MTSM's own FleetPy
  demand file the same way would also remove the order of the agent list as a factor, but it can change FleetPy's
  results, so it belongs to a new reference (not tested).
- **Also noticed, not changed:** the time sampler of the function is built from the requests of the input file only,
  i.e. the microtransit users of the iteration (68 in the reference). With 180 five-minute bins and a smoothing of
  0.5 per bin (90 in all) against 68 observed requests, 57 % of the new times are drawn uniformly over 5:00-20:00;
  the "trend" is mostly flat. The new request ids start at 60005; the largest id in the demand data is 15047, so
  they do not clash. Whether `update_network_files` mixes the synthetic requests into the waiting times it writes
  to the final networks was not checked.
- **Update 2026-11-25 (user's decisions): the block is now the switch `demand_upscaling`, on `main`, off by default.**
  - **Why the block exists (user):** a run on all travelers takes too long, so the model runs on a sample (`main`'s
    `demand/demand.csv` is a 25 % sample of about 15,000 travelers: 3,742 rows, ids up to 15,047; drawn with
    `sample_20_percent` in `pre_process/generate_demand_files.py`, `frac=0.25`). With only the sample's requests the
    microtransit fleet is less busy than with all travelers and the system looks better than it is. The synthetic
    requests make FleetPy serve as many requests as all travelers would; the results are then scaled to all travelers
    (until now by the optimizer's commented-out block "USE THIS PART WHEN THERE IS MICRO UPSCALING HAPPENING": 4 x the
    FRT and microtransit revenues, 4 x the logsum delta). Car times do not depend on the number of travelers (fixed
    period networks; the `flow` field of `network_algorithms.Link` is never used) and the FRT has no capacity, so only
    FleetPy needs the extra requests.
  - **Parameters** (model file): `demand_upscaling` (False), `demand_sample_share` (1; between 0 and 1 when on),
    `sample_demand_file` (`none`; a path relative to `mtsm_data/<area>/` when on). Off: the run reads
    `demand/demand.csv` as all travelers, nothing is added or scaled, and the reference is unchanged. On: the run reads
    the sample file, which the user provides (MTSM does not draw the sample); `tools/check_study_area.py` checks it as
    file 2. Code: `config.DEMAND_UPSCALING`, `DEMAND_SCALE` (1 / share), `scale_up`; `mtsm_paths.run_demand_file`.
  - **FleetPy** (`microtransit.py`, `synthetic_demand.add_synthetic_requests`, each iteration before FleetPy):
    round(n x (1 / share - 1)) synthetic requests for the n requests of the sample (3 n for 0.25). Request ids from
    `synthetic_id_start`: the smallest power of ten >= 10 x max(largest traveler id + 1, travelers / share), so clear
    of every traveler's id, also of the travelers outside the sample if the full demand numbers them alike (Lemon Grove:
    1,000,000; was 60,005); the run stops if an MTSM request id (including the next free ids of a traveler's later
    microtransit legs) reaches it. Times only in the scenario's microtransit operating periods (was 5:00-20:00 for
    every scenario: a scenario with fewer periods would have got requests while no service runs, raising the
    rejection rate). The whole file is written sorted by `rq_time` (stable sort): **the fix of this item** for the
    synthetic rows. Seed: the run's `random_seed`, the same in every iteration (was 42). The way times and pairs are
    drawn is unchanged; its review is I-45. `synthesize_requests_with_trend_time` was split into `make_time_sampler`
    (now with windows), `make_od_sampler` (unchanged) and `synthesize_requests`; its file handling and the "+ 5" of the
    ids are gone.
  - **What MTSM reads back from FleetPy includes the synthetic requests, on purpose:** the waiting time per period and
    the detour ratios (`update_network_files`, all rows of `1_user-stats.csv`), the rejection rate and waiting time
    (`standard_eval.csv`), and the fleet's miles, utilization, occupancy and speed. They stand for the travelers outside
    the sample. (A first proposal on 2026-11-25 to use only the sample's rows was withdrawn.)
  - **Evaluation file** (`results.py`; both columns): the sums over the sample's travelers are multiplied by 1 / share:
    traveler and trip counts, revenues, out-of-pocket, gas and parking costs, generalized cost, the logsum increase,
    mode switches, car, walk and passenger miles, walk and waiting times. The values built from them then describe all
    travelers: `tot_sub` and the twelve `sub_per_*` lines, `M_PMT/M_VMT`, `F_PMT/F_VMT`, `tt_VMT`. Not scaled: the FRT
    schedule's cost and miles and FleetPy's values (already for all travelers), and shares and averages (a ratio of
    two scaled sums). A last line `demand_sample_share` is added only when the switch is on. The FRT link ridership
    files (`debug_False_..._transit_edges_rders_scen_10.csv`) are scaled too; the individual results stay one row per
    traveler of the sample, unscaled.
  - **Found on the way: `main`'s results mix scales today** (switch off, 25 % sample): `tot_sub` and the `sub_per_*`
    lines set the full FRT and fleet costs against a quarter of the revenues and riders, `M_PMT/M_VMT` and
    `F_PMT/F_VMT` are a quarter of their value, `tt_VMT` adds the sample's car miles to the full transit miles, and the
    optimizer's active objectives (`-(x1 - x2)`, `y1 - y2`) inherit this. User's decision: the reference is not
    updated; the switch is tested on `main`.
  - **Optimizer:** the commented-out block was removed (comment at its place). With the switch on, the evaluation
    file gives the values the block computed: `tot_sub` (scenario) - `tot_sub` (base) = its subsidy delta, and the
    logsum line is 4 x the sample's. Notes: candidate copies are made from the frozen model file, so an optimizer run
    with the switch on needs it set in the frozen file (then `python tools/check_inputs.py --write <area>`); the
    hypervolume `ref_point` (-18000, 0) is in the evaluation file's scale and may need a new value for all travelers
    (not changed).
  - **Not done:** sorting MTSM's own FleetPy demand file when the switch is off (it would change FleetPy's results:
    a new reference, the branch `TRA_resubmission`).
  - **Checks (2026-11-25):** the new functions on a copy of the reference's last FleetPy demand file (68 requests):
    204 added, ids 1,000,000-1,000,203, times 5:03-19:56, file sorted, the same file from a second call, and a stop
    when an id reaches the start. A full run with the switch on (a copy of the model file with `demand_upscaling`
    True, `demand_sample_share` 0.25, `sample_demand_file` `demand/demand.csv`; 8 min 54 s, 8 iterations): FleetPy got
    68 + 204 requests in iteration 0, then 49 + 147; the evaluation file against the individual results (script in
    the session scratchpad): `tt_agents` 14,968 = 4 x 3,742 in both columns; car and transit users, out-of-pocket
    cost, logsum increase (2,790.30), microtransit, FRT and car miles = 4 x the sums of the individual rows; `tot_sub`
    = costs - revenues in both columns (scenario 6,029.86, base 2,190.37); `M_PMT/M_VMT`, `F_PMT/F_VMT`, `tt_VMT`,
    `sub_per_M_trip` and `M_avg_wait_time` consistent; ridership files in multiples of 4; last line
    `demand_sample_share` 0.25. A full run with the switch off: `compare_reference.py` printed **`REPRODUCED`**.
- **Update 2026-11-25, later (I-45, user's decision):** the drawing from the time-of-day profile was replaced by
  copies of the sample's requests (time shifted by up to +-15 min within the period, origin and destination each a
  virtual stop within 400 m walking distance; parameters `synthetic_time_shift_min`, `synthetic_stop_radius_m`).
  The time windows of the operating periods above are no longer used: a copy stays in its request's period.
- **Resolution (2026-11-25, user's decision):** closed. The synthetic requests are now the switch
  `demand_upscaling` (update 2026-11-25 above; how they are made: I-45, closed), and with the switch on the whole
  FleetPy demand file is written sorted by `rq_time`, so the order within a time step follows the request times.
  With the switch off nothing changes: every scaling step is behind the switch (`config.scale_up` returns its
  argument), the evaluation file has no extra line, no request is added and no file is sorted; two full runs with
  the switch off printed `REPRODUCED` (26 files). The user tests the switch on `main`. The remaining point, sorting
  MTSM's own FleetPy demand file when the switch is off, moves to I-47 (with the new reference on the branch).

### I-45: How the synthetic FleetPy requests are drawn (`demand_upscaling`): flattened time profile, time and direction drawn apart, repeated stop pairs
- **Status:** Closed (2026-11-25); Decision needed until then (user, 2026-11-25: leaning towards option (b), wants
  more information first). **Severity:** Medium. **Found:** 2026-11-25 (review of I-32).
- **What:** `synthetic_demand.synthesize_requests` (the user's method, unchanged by I-32) draws each synthetic request
  from the sample's microtransit requests of the iteration:
  1. **The time profile is mostly flat.** The time comes from 5-minute bins with a smoothing of 0.5 per bin. With
     180 bins (15 h of service) the smoothing adds 90 made-up requests; against 68 real requests (the reference's last
     iteration) 57 % of the synthetic times are drawn uniformly over the service hours, and the peaks flatten.
  2. **Time and origin-destination pair are drawn apart, and half the pairs are reversed** (`od_mode` "ordered",
     `swap_prob` 0.5): a morning trip's pair can come back at noon, in the other direction; the pattern of the
     directions over the day (inbound in the morning, outbound in the evening) is lost.
  3. **The pairs repeat the sample's stop pairs exactly:** the synthetic requests share origins and destinations with
     the real ones more than the requests of all travelers would, so FleetPy pools them more easily; occupancy and
     waits may come out somewhat optimistic. Built into any resampling of the sample; at most reduced.
- **Options:**
  - (a) keep the method; smaller smoothing (or none), so the profile follows the sample.
  - (b) copy each real request (1 / share - 1) times, with its time shifted at random by up to +-N minutes (inside
    its period and the service hours), same pair and direction; with a non-whole factor, the remainder by random
    rounding. Keeps the time-place-direction pattern and gives exactly the factor. Open: N; whether to move the stops
    to nearby nodes as well (point 3).
- **To do:** the user decides; then a test run on `main` with the switch on (no reference change: the switch is off
  there).
- **Measured 2026-11-25** (the 68 requests of the reference's last FleetPy file, 204 synthetic; real: AM 13, MD 35,
  PM 20, 68 different stop pairs, none shared by two requests): the current method gave AM 50 / MD 79 / PM 75
  (3 x real would be 39 / 105 / 60), an hourly profile 40 % off the real one, 54 % of the synthetic requests reversed,
  18 % with the pair, direction and period of a real request. Plain copies (b) fix all of this (exactly 3 x per period;
  100 % same pair and direction), but 87-100 % of them then have a request on the same stop pair within 10 min
  (current method: 5 %), which FleetPy can pool for free. Moving the copies' stops removes that: with a random virtual
  stop within 400 m walking distance (a median of 14 stops, at least 3, around a real origin) 1 % remain.
- **Resolution (2026-11-25, user's decisions: the recommendation for all points):** option (b) with nearby stops.
  `synthetic_demand.py` rewritten (`synthesize_requests`, `NearbyStops`; the old samplers are in the git history):
  each request of the sample gets 1 / share - 1 copies (a factor that is not whole: random rounding per request); a
  copy's time is the request's time + a random shift of up to +- `synthetic_time_shift_min` (15) minutes, reflected
  into the request's time period; its origin and its destination are each a random virtual stop within
  `synthetic_stop_radius_m` (400) m walking distance on the walk links of the scenario's super-network (the request's
  own stop included; drawn again if both are the same node; the request's stops if there is none). Each request's
  copies have their own generator, seeded with (`random_seed`, request id): they change only when that request
  changes. Both parameters are in the model file (`mtsm_data/MANIFEST.csv` rewritten). Walking distance, not straight
  line, because the coordinates of Lemon Grove's FleetPy nodes are in feet (I-39). Checks on the 68 requests: 204
  copies, 39 / 105 / 60 per period, no copy with a real request's exact pair, 1 % with a same-pair request within
  10 min, shifts within 15 min, reproducible, dropping one request leaves the other copies unchanged, share 0.3 gives
  159 copies (158.7 expected).
- **Comparison runs (2026-11-25; switch on, share 0.25, `demand/demand.csv` as the sample; FleetPy values of the
  last FleetPy run of each):**

  | | current method | (b) plain copies (R = 0) | (b) with nearby stops (R = 400 m) |
  |---|---|---|---|
  | iterations; FleetPy requests at the end | 8; 49 + 147 | 7; 62 + 186 | 8; 50 + 150 |
  | shared rides | 6.7 % | 65.4 % | 39.4 % |
  | occupancy | 0.42 | 0.77 | 0.65 |
  | FleetPy waiting time, mean / median (s) | 349 / 265 | 296 / 201 | 370 / 256 |
  | rejection rate | 0.5 % | 0.8 % | 3.5 % |
  | fleet miles `M_VMT` | 380.3 | 295.6 | 279.3 |
  | `M_trips` (all travelers) | 196 | 248 | 200 |
  | `tot_sub ($)` | 6,029.86 | 5,337.77 | 6,036.92 |
  | `tt_mob_lgsm_inc_with_micro` | 2,790.30 | 3,013.12 | 2,600.24 |

  Plain copies pool most riders with their own copies: waits fall, microtransit looks better, 27 % more microtransit
  trips and a lower subsidy. With nearby stops the sharing is between the two, and the waits and the rejection rate
  are the highest: a busier fleet, as intended. The current method's scattered times and pairs give little sharing
  but more fleet miles. Which comes closest to all travelers is not known: a run on all travelers against a run on a
  sample with the switch would tell (possible on the branch, whose demand has 42,698 travelers).
  A full run with the switch off: `compare_reference.py` printed **`REPRODUCED`** (26 files).
- **Found on the way:** 21 of the 68 real requests start at a node without a microtransit boarding link: I-46.

### I-34: Downtown San Diego and the new FRT network: the FRT code works only for Lemon Grove
- **Status:** Closed (2026-11-25); Open until then. **Severity:** High (blocked a planned run: downtown San
  Diego). **Found:** 2026-11-23 (planning the
  FRT network from SANDAG's ABM3 transit data, in the input-preparation repository `TRA_input_data_prep`).
- **Plan (user, 2026-11-23):** the model is to be made general in the study area, so that it runs for Lemon Grove and
  downtown San Diego. The FRT network of both areas will be rebuilt from SANDAG's ABM3 transit network
  (`EMMEOutputs.gdb`: `trrt`, `trlink`, `trstop`; the 2022 network of the ABM3 run behind the demand files), as
  `pre_process/build_super_network.py` inputs (`frt_stops.csv`: `stop_id,pos_x,pos_y`; `frt_edges.csv`:
  `from_stop,to_stop,distance,travel_time,route`). Decisions for that network:
  - **One stop node per stop, route and direction** (several stop nodes can share one walk node). No two FRT links
    share a node pair.
  - **`route` = the route number** (4, 520, 856, ...), both directions; the direction is in the stop nodes.
  - **Run time = the distance along the route / 30 mph**, buses and rail alike (as the old network and
    `frt_speed_mph`).
  - **One headway for all routes** (as now: `frt_headway`, boarding waits half of it). The ABM3 headways per route
    and period are not used.
  - **One variant per route and direction**; downtown leaves out the peak-only routes 110, 280 and 290. Routes with
    one stop in the area (Coaster 398, 598, airport 994) have no link and drop out.
  - **Each stop is joined to a street node** of the new road network (never a freeway node; I-33). The stop's
    `pos_x/pos_y` are that node's coordinates, so `nearest_walk_nodes` finds it at 0 m.
- **FRT plan, update (2026-11-23, later the same day):**
  - The stop rule is now "a stop counts if it lies within 50 ft of the study area", so stops on boundary streets
    count.
  - As a result the airport route 994 (downtown) and route 851 (Lemon Grove) have links. Only 398 and 598 drop out.
  - A route's line past its last stop inside the area is not in the network (e.g. the Lemon Grove trolley, route
    520, west of Massachusetts Av station). Trips inside the area are not affected.
  - Built 2026-11-23:
    - Lemon Grove: routes 4, 520, 851, 856, 916, 917, 936; 12 variants, 122 stop nodes, 110 links.
    - Downtown: 21 routes; 41 variants, 354 stop nodes, 326 links.
- **What in the model is Lemon Grove only or assumes the old FRT network** (checked at `008c6ac`):
  1. **FRT line length, duration, operating cost, VMT and ridership output.**
     `output_performance_metrics.get_transit_line_dist`, `get_transit_line_duration`, `get_transit_link_info` and
     `write_fixed_transit_link_vmt` set their input file only under `if study_area == "lemon_grove"`. For any other
     area the file name is undefined, and `scenarios.py:90` stops with `UnboundLocalError`. They read the old file
     `mtsm_data/lemon_grove/transit/super_network_transit_edges.csv` (columns `distance (meters)`, `route`), not the
     new FRT edges.
     - The line length is the sum of the *unique distance values* of a route's links. This halves the length only
       because the old network copied each link into both directions with the same distance. In the ABM3 network the
       two directions have different paths and distances, so the length would come out about 2 x, and the cost
       formula multiplies by 2 again.
     - The number of stops counts the from-nodes of both directions.
     - Needed: a per-route length and stop count that the new network supplies (e.g. a route table written with the
       FRT files), and the area's file paths.
  2. **FRT fare and microtransit start fare.** `generalized_cost_dijsktra_OD_heap` (`network_algorithms.py:352` and
     `:372`) sets them only under `if study_area == "lemon_grove"`. In any other area every FRT boarding and every
     microtransit start costs $0, so FRT and microtransit revenue are 0.
  3. **Parallel links are lost without a message.** `read_super_network` builds an `nx.DiGraph`. A second link with
     the same `(from_node, to_node)` overwrites the first (route, time, link type). The planned FRT network has no
     such pairs. Still, a check that stops on duplicate pairs would catch any input that has them.
     - 2026-11-23: a test build in `TRA_input_data_prep` with the new inputs has no duplicate `(from_node, to_node)`
       pairs. The duplicate-link check is still worth adding.
  4. **A route change becomes a transfer.** With stop nodes per route, a change at the same stop is alighting (type
     2, 0 s) and boarding (type 2, half the headway). The boarding pays no new fare, because `transit_fare` is not
     set when the previous link is a waiting link. It adds `bt_f_trfer` when the transfer penalty is on
     (`IsFixedLink`). The "route change at a shared stop" rule (`route != route_pre`, line 349) and its handling in
     `trip_legs.py` no longer apply. The old network had no wait for this change, so results change; this belongs
     to a new reference. I-31's label problem does not arise (every FRT link has exactly one route); I-25 can be
     decided on the new network.
  5. **Other places that name Lemon Grove:** a search for `"lemon_grove"` / `LG_` finds 70 lines, in
     `output_performance_metrics.py` (27), `mtsm_paths.py` (14), `update_network_files.py` (7),
     `folder_directory.py` (6), `fleetpy_runner.py` (6), `update_initial_network.py` (3), `network_algorithms.py` (2),
     `get_microtransit_skims.py` (2), `config.py` (2) and `scenarios.py` (1). Also per area:
     - `num_walk_nodes`, `microtransit_node_offset` and `micro_only_max_walk_node` in
       `mtsm_constant_configurations.csv` (I-13);
     - the FleetPy network and staged inputs (`fleetpy_runner.LG_STAGED_INPUTS`).
     - 2026-11-24: the accessibility calculation was removed (I-37); `output_performance_metrics.py` went from
       1,035 to 197 lines and the region and MGRA paths are gone from `mtsm_paths.py`.
     - 2026-11-24 (`docs/study_area_plan.md`, Phase 1 step 1): the `LG_*` constants are replaced by
       `mtsm_paths.area_paths(area)`; the branches that only chose a folder are gone (`folder_directory`,
       `get_transit_line_dist`, `get_transit_link_info`, `write_fixed_transit_link_vmt`, `get_node_ct`,
       `update_network_files`), so item 1's `UnboundLocalError` no longer occurs.
       `fleetpy_runner.LG_STAGED_INPUTS` is `staged_inputs(area)`. Still for Lemon Grove only (Phase 2): the fares
       (item 2), the type-5 update (item 6), the FRT line duration and the ridership file's `travel_time`, the
       file names in `update_initial_network.py`, `lemon_grove_vehtype` in `create_config_files`, and the startup
       check.
     - 2026-11-24 (Phase 1 step 2 and Phase 2 step 1): all of these are gone. The file names come from
       `mtsm_paths.area_paths`; the fares (item 2), the type-5 update (item 6), the FRT line duration and the
       ridership file's `travel_time` apply to every area; `<area>_vehtype`; the startup check accepts any area.
       Items 1 (line length from the new FRT network), 3 (duplicate-link check, Phase 4) and 4 remain.
     - 2026-11-24 (Phase 3 step 1; user's decision (b2)): item 1 is done. The FRT line length and stops come from
       the route table `networks/frt_routes.csv`, in the format `TRA_input_data_prep` writes (one row per route and
       direction); the costs add up the rows. Lemon Grove's table gives each direction half of the route's link
       distances: routes 856 and 916 had lost a link of equal length under the old distinct-distance rule (3,508 m
       -> 3,702 m, 1,647 m -> 1,844 m). Reference updated (FRT vehicle miles +2.41 %, FRT operating cost +0.52 %).
  6. **Microtransit waiting times** (found 2026-11-23, checked at `a912056`).
     - MTSM uses `aggregation,whole_region` (constant configuration), and the user confirms this is the branch to
       keep.
     - Even so, `update_network_files.update_network_files` calls `get_microtransit_skims.get_node_ct(study_area)`.
       That function reads `pre_nodes.csv` (columns `census_tract`, `node_in_fleetpy`) only from the Lemon Grove
       folder (`LG_TRANSIT_NETWORK_DIR`; there is no path for other areas), and it looks up a tract for every type-5
       link.
     - The new networks' `pre_nodes.csv` (`TRA_input_data_prep`) has these columns, with `census_tract = 0` for every
       node. The whole-region branch therefore works on them once the path is per area. No census tract data is
       needed.
     - 2026-11-24: with `whole_region`, `get_node_ct` no longer reads `pre_nodes.csv`; every walk node is in one
       zone (decision G, `docs/study_area_inputs.md`). The file is read only with `census_track`.
     - In the "micro" branch, the type-5 links are updated only `if study_area == "lemon_grove"`
       (`update_network_files.py:340`). In any other area they keep the initial 180 s. The micro_only branch uses
       `micro_only_max_walk_node` (I-13).
- **Impact:** a downtown San Diego run cannot start (item 1). Once it starts, its FRT and microtransit fares are 0
  (item 2), and its microtransit waiting times stay at the initial 180 s (item 6). In both areas the new FRT network
  changes transfers (item 4) and needs the line cost fixed (item 1).
- **To do:**
  - make the study area a setting that selects the paths, the node ranges and the FleetPy inputs;
  - remove the `if study_area == "lemon_grove"` branches (fares for every area);
  - compute line length and duration from the new FRT network;
  - add a duplicate-link check to `read_super_network`;
  - microtransit waiting times for every area (item 6): the `pre_nodes.csv` path per area in `get_node_ct`, and the
    type-5 update in `update_network_files` without the Lemon Grove condition;
  - rebuild the Lemon Grove reference with the new road and FRT networks;
  - see also I-14 (downtown code in the old preprocessing), I-24 (transfer fare rules), I-33 (freeways) and I-35
    (one super-network per time period).
- **Resolution (2026-11-25, user's decision):** closed; the model no longer assumes Lemon Grove or the old FRT network
  (`docs/study_area_plan.md`, Phases 1-4 and 7, 2026-11-24). Item by item:
  1. FRT line length, stops, cost and ridership output: from the route table `networks/frt_routes.csv` in
     `TRA_input_data_prep`'s format (Phase 3 step 1; reference updated 2026-11-24).
  2. FRT fare and microtransit start fare: for every area (Phase 2 step 1).
  3. Duplicate `(from_node, to_node)` pairs: `tools/check_study_area.py` warns at startup (Phase 4, decision E);
     `read_super_network` still keeps the last link of a pair.
  4. A route change on TRA's network is an alighting and a boarding: handled on the branch `TRA_resubmission` with
     I-25 (transfer penalty on) and I-44 (fare rules: every boarding pays; whether a route change at a shared stop
     pays).
  5. Paths and names: `mtsm_paths.area_paths(area)`, `staged_inputs(area)`, `<area>_vehtype`; the startup check
     accepts any area (Phases 1-2). The node ranges per area: I-13, closed 2026-11-24.
  6. Microtransit waiting times: the type-5 update and the whole-region zone for every area (Phase 2 step 1).
  Not part of this item: the downtown San Diego run itself, which needs downtown's inputs from `TRA_input_data_prep`
  (next area in `docs/study_area_plan.md`), and the downtown parts of the old preprocessing (I-14).
### I-19: The microtransit start fare always gets the FRT-to-microtransit transfer discount
- **Status:** Closed (2026-11-25); Open until then. **Severity:** Low. **Found:** 2026-11-09 (dropping fare scenarios 0-9).
- **What:** in the fare structure (the former fare scenario 10, `network_algorithms.generalized_cost_dijsktra_OD_heap`),
  the microtransit distance fare is multiplied by `Fixed2MicroFactor` only after an FRT trip leg (`IsFixedLink`),
  but the start fare at a microtransit waiting link is always multiplied by `Fixed2MicroFactor` (and by the peak
  factor), also when no FRT leg came before.
- **Impact:** none in the reference run (`Fixed2MicroFactor = 1`). When the optimizer sets `Fixed2MicroFactor` below
  1, every microtransit trip gets the transfer discount on its start fare, not only trips after FRT.
- **To decide:** is this intended? If not, apply the factor to the start fare only after an FRT leg, like the
  distance fare. This changes results for `Fixed2MicroFactor != 1` (not the reference).
- **2026-11-25 (I-24):** the distance fare now gets `Fixed2MicroFactor` on the first microtransit ride after an FRT
  ride only (in `network_algorithms.transit_label_search`); the start fare still always gets it. Still open.
- **Resolution (2026-11-25):** user's decision (option 1 of three: the factor on the start fare only after an FRT
  ride; or keep it as a general microtransit discount; or never on the start fare): the start fare gets
  `fixed2micro_factor` only on the first microtransit ride after an FRT ride, like the distance fare, so the whole
  transfer discount follows the rule of I-24 (`network_algorithms.transit_label_search`, the microtransit boarding
  link; the label already holds whether an FRT ride came before). Checked on made-up paths (FRT fare 3 $, start fare
  2 $, 1 $ distance fare per ride), old and new code: with `fixed2micro_factor` 0.5 a microtransit-only trip pays
  3.0 $ (before 2.0 $), FRT -> microtransit 1.5 $ as before, microtransit -> FRT -> microtransit and FRT ->
  microtransit -> walk -> microtransit 4.5 $ (before 3.5 $: only the ride after the FRT is discounted); with the
  factor 1 all fares are unchanged. With `micro2fixed_factor` 0 the floor of I-24 counts the microtransit fare paid,
  so the FRT boarding in microtransit -> FRT -> microtransit became free (1.0 $ before), since the first ride now
  costs the full 3 $. No effect on the reference (`fixed2micro_factor` 1; the optimizer does not vary it): full run
  `REPRODUCED`.

### I-17: Travelers who keep their transit choice resubmit only their last microtransit and FRT leg
- **Status:** Closed (2026-11-25); Open until then. **Severity:** Medium. **Found:** 2026-11-09 (restructuring the entry script, step 4).
- **What:** in an iteration, a traveler whose transit probability changed by at most `MODE_CHANGE_THRESHOLD` keeps
  the previous choice (`change_mode == False`). If that choice was transit, `run_examples_new_parking.py` writes the
  traveler's previous microtransit request to the FleetPy demand file and the previous FRT trip to the FRT demand
  file again. But `state.pre_iter_M_info` and `state.pre_iter_F_info` hold one leg per traveler: each leg of the
  path overwrites the previous one. A traveler with two microtransit legs therefore sends one request to FleetPy,
  while `num_M_trips` still counts two trips (`ag_num_M_trips`), and the waiting time is the period average of the
  last leg times the number of legs. The same holds for FRT legs.
- **Impact:** unknown: it depends on how many travelers have more than one microtransit or FRT leg and keep their
  choice. FleetPy then sees less demand than the model counts. Not checked in the reference run.
- **To decide / fix:** if each leg should be resubmitted, keep a list of legs per traveler (`pre_iter_M_info[rq_id]`
  as a list) and write all of them. This changes the FleetPy demand and the results, so it needs a new reference.
  First count how often it happens in the reference run.
- **Count in the reference of 2026-11-25 (before the fix):** no traveler's transit probability changed by more
  than the threshold after iteration 0 (the run log prints 0 in every iteration), so from iteration 1 on every transit
  user resubmitted stored legs. Of 301 transit users, one had two legs of a kind: traveler 11650 (PM), two FRT legs,
  so the FRT demand file listed 24 legs while `F_trips` counted 25. No traveler had two microtransit legs, so FleetPy's
  demand was complete (68 requests = `M_trips` 68). The FRT demand file is written only; the model does not read it.
  A second, smaller fault: the stored legs were never cleared, so a traveler whose new transit path had no
  microtransit (or FRT) leg would have resubmitted the old one (not hit in the run).
- **Resolution (2026-11-25):** user's decision: fix on `main` before the branch `TRA_resubmission` fast-forwards to it
  (on TRA's network every route change makes a second FRT leg). `mtsm_model/iteration.py`: when a traveler chooses
  transit, `state.pre_iter_M_info[rq_id]` and `state.pre_iter_F_info[rq_id]` start as empty lists and get every leg of
  the path; a traveler who keeps the transit choice resubmits every leg (each microtransit leg gets its own free
  FleetPy request id, as before), and the microtransit wait is the sum of the period averages of the legs (before:
  the last leg's period average x the number of legs; the same for one leg). `mtsm_model/state.py`: comments. A full
  run differed from the reference only in the FRT demand file: one row more, `63287,1107,1101,11650` (the first FRT
  leg of traveler 11650); no reported value changed. The file was replaced by the run's; a second full run printed
  `REPRODUCED`.

### I-24: Transfer fare rules: the discount lasts for the whole trip; re-boarding after microtransit is charged
- **Status:** Closed (2026-11-25); Open (to decide) until then. **Severity:** Low. **Found:** 2026-11-11 (checking the FRT <-> microtransit transfers).
- **What:** the fare rules of `network_algorithms.generalized_cost_dijsktra_OD_heap` at an FRT boarding (walk node ->
  stop, link type 2; since I-23 the discount is set only there):
  1. **The discount holds for the rest of the trip.** The condition is `IsMicroLink`: the path has used microtransit
     *anywhere before*, not just before this boarding. In microtransit -> FRT -> walk -> FRT, the second FRT boarding
     is also discounted (`transit_fare_set * Micro2FixedFactor`), although the rider comes from a bus. Likewise
     `IsFixedLink`: after any FRT leg, every later microtransit link gets `Fixed2MicroFactor`.
  2. **Re-boarding at a shared walk node.** A boarding right after an alighting at the same walk node
     (`link_type_pre == 2`) pays no FRT fare: a free FRT -> FRT transfer. After a microtransit leg the discounted
     fare is charged on that re-boarding instead, so the rider pays more than a rider without microtransit
     (unless `Micro2FixedFactor` is 0). Transferring by walking to another stop pays the full fare again.
- **Impact:** none in the reference run (`micro2fixed_factor` 0, `fixed2micro_factor` 1). Affects the optimizer's
  candidates with other factors: the price of trips with more than one FRT boarding after microtransit, or with
  microtransit after FRT.
- **To decide:** (1) is the discount meant for the whole trip, or only for the boarding right after the other mode
  (then the condition is the previous leg's mode, not "used before")? (2) Should a re-boarding after an alighting
  stay free also after microtransit (move the discount inside `if link_type_pre != 2:`)? Neither changes the
  reference, so a full run with `REPRODUCED` confirms the change; check the fares with factors other than 0 and 1
  as for I-23. Related: I-19 (start fare), I-22 (search), I-25 (transfer penalty).
- **Resolution (2026-11-25):** user's decisions after the trial of 2026-11-25 (`docs/pathfinding_code_update.md`):
  1. **The discount for the next boarding only:** `micro2fixed_factor` applies to the first FRT boarding after a
     microtransit ride; `fixed2micro_factor` to the distance fare of the first microtransit ride after an FRT ride.
     The start fare is still always x `fixed2micro_factor` (I-19, open).
  2. **No free FRT -> FRT re-boarding:** every other FRT boarding pays the full fare, also a boarding right after an
     alighting at the same walk node (it was free). Confirmed with the user: in microtransit -> FRT -> FRT the second
     boarding pays the full fare.
  3. **A floor against very short microtransit rides bought only to make the FRT fare free:** the discounted boarding
     pays at least the FRT fare minus the microtransit fare paid since the last FRT boarding,
     `F - min(M, (1 - micro2fixed_factor) F)`, so microtransit + FRT never cost less in fare than the FRT alone. Chosen
     over a fixed factor (0.5 was tried) because it holds for every optimizer candidate (`micro2fixed_factor` and the
     fares vary there; a factor closes the loophole only above 1 - start fare / FRT fare, about 0.34 in the
     reference).
  With the exact search (I-22), on the reference's final networks, least-cost paths with a microtransit ride under
  30 s: 211 (whole-trip discount), 162 (next boarding only), 19 (with the floor; these can only be chosen for time,
  since the fare is no lower). Rule 2 changed no base-case path on Lemon Grove's network (a route change there is
  mostly at a shared stop node, without a boarding link; I-44). In `network_algorithms.transit_label_search`;
  checks, the new reference and its second run `REPRODUCED`: I-22. Revisit on the branch: I-44.

### I-22: The path search can miss the least-cost path when a transfer discount applies
- **Status:** Closed (2026-11-25). **Severity:** Medium. **Found:** 2026-11-11 (checking the FRT <-> microtransit transfers).
- **What:** in `network_algorithms.generalized_cost_dijsktra_OD_heap` the cost of a link depends on the path before
  it: after a microtransit leg the FRT fare is multiplied by `Micro2FixedFactor`, after an FRT leg the microtransit
  distance fare by `Fixed2MicroFactor`, and a boarding right after an alighting (shared walk node) pays no FRT fare.
  The search keeps one path per node (Dijkstra), so at a node it keeps the cheapest path so far and drops a dearer
  one that would make the rest of the trip cheaper, e.g. a microtransit leg that makes the following FRT ride free.
- **Impact:** checked on the reference run's final networks (AM-PM, 3,472 travelers) against an exact search with
  one label per (node, microtransit used, FRT used, previous link FRT waiting) and the same link costs: with the
  reference factors (`fixed2micro_factor` 1, `micro2fixed_factor` 0) the model's transit path is not the least-cost
  one for **405 travelers (11.7 %)**; mostly an FRT-only path where microtransit + FRT is cheaper (275). With both
  factors 0.5: 49 travelers. Paths, costs, mode choice and all results depend on it.
- **Fix:** search over the states (node, microtransit used, FRT used, previous link FRT waiting) instead of nodes
  (up to 8 labels per node; slower). Changes results: make and document a new reference in
  `docs/reference_results/`; together with the other changes that need one (I-19, I-21, I-25).
- **Update 2026-11-14:** the fix was tried and taken back (user's decision: not now; nothing of it is in the code).
  Record of the trial: `docs/pathfinding_code_update.md`. The label search gave a cheaper path for the 405 travelers
  and changed the totals little, but it shows a loophole of the fare rules (very short microtransit rides that make
  the FRT fare free; I-24). To be decided together with the fare rules.
- **Update 2026-11-25:** tried again in copies of the repository (outside it, `D:\Ritun\MTSM_fare_test`), with the
  fare rules of I-24: seven variants (today's rules, the new rules, the new rules with a fare floor or with
  `micro2fixed_factor` 0.5, each with one path per node and with the exact search). Record in
  `docs/pathfinding_code_update.md`, section "2026-11-25". The lower logsum of 2026-11-14 is explained there: it comes
  from FleetPy's longer waiting times (more microtransit trips), not from the search; on the same networks the exact
  search raises the logsum (+3.0).
- **Resolution (2026-11-25):** user's decision: the new fare rules with the floor (I-24) and the exact search, on
  `main` with a reference update. `network_algorithms.transit_label_search` (called by
  `generalized_cost_dijsktra_OD_heap` for mode `"T"`) keeps the least-cost path per label: the node, whether a
  microtransit ride came since the last FRT boarding (if `micro2fixed_factor` != 1), whether an FRT ride came since
  the last microtransit alighting (if `fixed2micro_factor` != 1), and, with the transfer penalty on (I-25), whether
  transit was used and the route of the FRT link into the node. Because of the floor, two paths with the same label
  are compared on two values (the cost, and the cost minus `bt_t_fr` x min(M, D); M the microtransit fare since the
  last FRT boarding, D the largest FRT discount), and a path is dropped only if another is at most as large on both.
  It returns the values at the destination and the finished trajectories (`paths.frt_path` / `micro_path` take them
  as they are). The car search is unchanged (car links only; it now stops at any other link type). Checks: the
  search code run with today's rules reproduced the reference (`REPRODUCED`); on fixed networks, for every traveler
  and variant, the cost and fares of the path recomputed link by link by separate code (no mismatch), the cost equal
  to an independent search over the full path state for 240 travelers per variant, and never dearer than the search
  with one path per node; the run on `main` gave the trial's files (25 of 26 byte for byte, `00_config.json` differs
  only in folder paths). New reference (14 files; `docs/reference_results/README.md`); a second full run printed
  `REPRODUCED`. Run time 396 s (before about 240 s). Revisit on the branch: I-44.

### I-38: Outside the microtransit operating periods, scenario travelers ride the FRT at the base headway
- **Status:** Closed (2026-11-24); Decision needed until then. **Severity:** High (can give wrong reported results,
  if not intended). **Found:** 2026-11-24 (writing the input specification, `docs/study_area_inputs.md`). Recorded on
  the user's request.
- **What:** `paths.networks_for_traveler` sets `T_F_network = initial_super_network["non_micro"][BASE_FRT_HEADWAY]`
  for every traveler. In a `micro` scenario, a traveler who departs outside the microtransit operating periods gets
  `T_micro_network = T_F_network`, so `paths.micro_path` routes their transit trip on the FRT network at
  `base_frt_headway` (Lemon Grove: 20 min, boarding wait 600 s) instead of the scenario's `frt_headway` (reference:
  10 min, 300 s). That search uses the scenario's fare (`cfg.transit_fare`), so the traveler gets the scenario's
  fare with the base case's headway. The scenario's FRT operating cost and vehicle miles are computed for
  `frt_headway` over all `frt_operating_hours` (19 h). (Using `T_F_network` with `BASE_FRT_FARE` for the base
  case's FRT path, `paths.frt_path`, is intended: I-28.)
- **Since:** the original code. `v1-reproducible`, `run_examples_new_parking.py` line 884, uses `base_FRT_headway`,
  with the scenario-headway version commented out just above it:
  `# T_F_network = initial_super_network["non_micro"][headway]  # the fixed route transit network remain constant - won't feedback to it`.
- **Impact:** in the reference the microtransit runs AM, MD and PM (5:00-20:00); 270 of the 3,742 travelers depart
  after 20:00 (EV). When the scenario's headway is shorter than the base headway (as in the reference), their
  transit cost is too high, so the transit share and the logsum for these travelers are too low; with a longer
  scenario headway, the other way round. Not quantified.
- **To decide:**
  - (a) Outside the operating periods, use the FRT network at the scenario's headway. The run already writes it
    (`initial_super_network_non_micro_hw_<headway>.csv`, `update_initial_network.py`) but does not read it.
    Changes results: its own reference update, or the batched new reference.
  - (b) Keep it, if the FRT is meant to run at the base headway outside the microtransit hours; then the FRT
    operating cost should be computed that way too.
- **Resolution (2026-11-24):** user's decision (a), on `main` with a documented reference update. In a `micro`
  scenario, a traveler outside the microtransit operating periods now rides the FRT-only network at the scenario's
  `frt_headway` (`initial_super_network_non_micro_hw_<h>.csv`, written by `update_initial_network`, now also read:
  `testing_scenario_creation.scen_create` and `networks.read_iteration_networks` keep it under its own key
  `frt_scenario`, so it never replaces the base case's network when a scenario headway equals the base headway;
  `paths.networks_for_traveler` uses it). The base case (FRT at `base_frt_headway` and `base_frt_fare`, I-28),
  `micro_only` and the operating costs are unchanged. Full run against the reference: only the 121 EV travelers
  (departures after 20:00; 270 in all) changed, all in the scenario's individual results; the base case's individual
  results and the evaluation file's `FRT_only` column are identical, and FleetPy's inputs and results are unchanged.
  Their FRT wait is now 300 s (half of 10 min) instead of 600 s; car users 3,444 -> 3,441, transit users 298 -> 301 (3 EV travelers from car to transit), `F_trips` 22 -> 25,
  `F_revenue ($)` 65.08 -> 75.92, `tot_sub ($)` 7,806.04 -> 7,795.20 (-0.14 %), `tt_mob_lgsm_inc_with_micro` 903.05 ->
  912.09 (+1.00 %), in 34 values of the evaluation file's `FRT_and_micro` column. 4 reference files replaced (the
  evaluation file, the scenario's individual results and FRT ridership file, the FRT demand file); a second full
  run printed `REPRODUCED` (`docs/reference_results/README.md`).

### I-13: The `micro_only` scenario uses the downtown San Diego node limit
- **Status:** Closed (2026-11-24). **Severity:** Low. **Found:** 2026-11-08 (removing downtown San Diego, step 2).
- **What:** in `update_network_files.update_network_files`, the `micro_only` branch sets the microtransit waiting
  time only on waiting links with `from_node <= 731`, the last walk node of the downtown San Diego network, and
  without a study-area check. The `micro` branch uses `from_node <= 1098` for Lemon Grove.
- **Impact:** none on the current results: the run only uses `microtransit_running_scenarios = ["micro"]`. A
  Lemon Grove `micro_only` run would leave the waiting time of walk nodes 732-1098 at their initial values.
- **Fix:** decided to leave it for now (2026-11-08). If `micro_only` is needed: use the same Lemon Grove check as
  the `micro` branch, then test it. The user decided on 2026-11-09 to keep `micro_only` and `non_micro` as
  options in the restructuring (`docs/entry_script_refactor_plan.md`).
- **Resolution (2026-11-24):** user's decision 1 of Phase 2 (`docs/study_area_plan.md`): the `micro_only` branch of
  `update_network_files` updates the waiting time on the type-5 links from every walk node up to the area's last walk
  node (`config.LAST_WALK_NODE`, derived from the files: Lemon Grove 1098), like the `micro` branch. The parameter
  `micro_only_max_walk_node` (731; in the parameter file since 2026-11-10) was removed. The reference run does not use
  `micro_only`; full run `REPRODUCED`. Not tested: a `micro_only` run (it needs a network no area has, see
  `docs/study_area_inputs.md`).

### I-05: `FRT_headway = 20` overwrites a frozen network
- **Status:** Closed (2026-11-24). **Severity:** Medium. **Found:** 2026-10-23 (Phase 1b). This predates the
  reproducibility work.
- **What:** `update_initial_net_with_bayesian_headway()` (`update_initial_network.py`; in
  `pre_process/process_network.py` until 2026-11-08) writes
  `initial_super_network_non_micro_hw_{headway}.csv` into `mtsm_data/lemon_grove/initial_network/`. For headway 20 this is
  the frozen `initial_super_network_non_micro_hw_20.csv` (the fixed-route network at the base headway).
- **Impact:** a run or optimizer candidate with headway 20 changes a frozen input. The startup check and
  `tools/check_inputs.py` would then report it as changed, and later runs would read the rebuilt file instead of the
  original.
- **To decide:** is the overwrite intended? If not, give the rebuilt file its own name, or stop the run before it
  overwrites a frozen file.
- **Resolution (2026-11-24):** fixed by Phase 1 step 2 of `docs/study_area_plan.md` (user's decision 2 (a) there).
  The inputs moved to `mtsm_data/lemon_grove/networks/`; the base case reads the base-headway network from
  `networks/super_network_frt_base_headway.csv`, and the run writes its per-headway networks into `initial_network/`,
  which now holds only what the run writes. Checked: building the networks for headway 20 writes
  `initial_network/initial_super_network_non_micro_hw_20.csv` and leaves every input unchanged
  (`tools/check_inputs.py`); that file is byte-identical to the input (as for the overwrites before, e.g. by the
  optimizer's headway-20 candidates on 2026-11-12, which is why they went unnoticed). Full run: `REPRODUCED`.

### I-37: The Lemon Grove accessibility used downtown San Diego's node list
- **Status:** Closed (2026-11-24). **Severity:** High (wrong reported values). **Found:** 2026-11-23 (planning MTSM
  for any study area, `docs/study_area_plan.md`, item 7).
- **What:** `get_fleetpy_demand_nodes()` (`output_performance_metrics.py`) read `mtsm_data/region/pre_nodes.csv`.
  That file had 732 nodes (0-731, 497 demand nodes), narrower coordinates than Lemon Grove's, and the node range of
  downtown San Diego (last walk node 731). Lemon Grove's own file, `lemon_grove/transit/network_folder/pre_nodes.csv`,
  has 1,099 nodes (814 demand nodes). The list was the set of origins of the accessibility calculations and the set
  of nodes that get a zone's employment (`create_nodes_emp_dict`). Node numbers are local to a network, so the
  downtown flags do not match Lemon Grove's nodes: nodes 732-1098 were never origins and got no jobs; of the 1,062
  nodes of Lemon Grove's node -> MGRA mapping, 483 were demand nodes in the downtown file, 805 in Lemon Grove's.
- **Impact:** every `wghted_acc_emp_5/10/15_min` value and every per-zone `acc_super_network` file was computed on
  the wrong node set, in both columns, including the reference until 2026-11-24 (last values, FRT only / with
  microtransit: 107.60 / 249.99, 402.64 / 4184.02, 1031.14 / 6331.68). Nothing else used them: choices, costs and
  subsidies were not affected. Accessibility values reported from earlier runs should be treated as affected. Since
  when: unknown (the file came from `Data/0719_input` in Phase 1b).
- **Resolution (2026-11-24):** not fixed; the accessibility calculation was removed (user's decision; the user no
  longer uses it), and the downtown file with the other accessibility inputs. The last version is at git tag
  `last-with-accessibility`. See `docs/progress.md`, "Accessibility calculation removed".

### I-06: Accessibility uses a hard-coded network for its node list
- **Status:** Closed (2026-11-24). **Severity:** Medium. **Found:** 2026-10-23 (Phase 4 check).
- **What:** `create_nodes_emp_dict()` (`output_performance_metrics.py`) hard-codes `headway = 20` and `virstop = 100`
  and reads `mtsm_data/lemon_grove/initial_network_0719/initial_super_network_micro_hw_20_virstop_100.csv`, only to collect
  the set of node IDs. Nodes with no assigned employment get 0. The result feeds the `wghted_acc_emp_{5,10,15}_min`
  columns.
- **Impact:** none today. The file has the same 2269 nodes as the network the scenario uses
  (`initial_super_network_micro_hw_10_virstop_75.csv`). A future scenario with a different node set would get
  silently wrong accessibility numbers.
- **Fix:** take the node list from the network the scenario actually uses. If the node set is unchanged, the reference
  still reproduces; check with a full run and `compare_reference.py`.
- **Resolution (2026-11-24):** removed with the accessibility calculation (user's decision;
  `docs/study_area_plan.md`, step A; `docs/progress.md`, "Accessibility calculation removed"). `create_nodes_emp_dict`
  and the network file it read (`initial_network_0719/initial_super_network_micro_hw_20_virstop_100.csv`) no longer
  exist. Checked: full run after the reference update printed `REPRODUCED` (26 files). See also I-37.

### I-21: Three different meters-per-mile values (1609.34, 1609, 1.609 km)
- **Status:** Closed (2026-11-23). **Severity:** Low. **Found:** 2026-11-10 (one parameter file, `docs/constant_config_plan.md`).
- **What:** the code converts miles with three different values, now three parameters in
  `mtsm_constant_configurations.csv`: `meters_per_mile` 1609.34 (fares, gas costs, VMT; `config.MILE_METER`),
  `meters_per_mile_frt_lines` 1609 (FRT line lengths, `output_performance_metrics.get_transit_line_dist`) and
  `km_per_mile_fleetpy` 1.609 (FleetPy's vkm and km/h, `output_performance_metrics.get_fleetpy_eval_output_metrics`).
  They were kept apart so that the results stayed identical (user's decision 2: separate keys now, merge later).
- **Impact:** small differences in the FRT line durations and operating costs and in the microtransit VMT and speed
  reported from FleetPy (1609 vs 1609.34: about 0.02 %).
- **Fix (later, user's intention):** use one value (`meters_per_mile`, 1.60934 km) everywhere and remove the two other
  keys. This changes results: make and document a new reference in `docs/reference_results/`.
- **Resolution (user's decisions 2026-11-23: now, with a reference update; keep 1609.34, not the exact 1609.344;
  FleetPy's km per mile = `meters_per_mile` / 1000; remove the two keys):**
  `output_performance_metrics.get_transit_line_dist` and `get_fleetpy_eval_output_metrics` use `config.MILE_METER`;
  `meters_per_mile_frt_lines` and `km_per_mile_fleetpy` removed from the parameter file and
  `mtsm_global_parameters.py`; `MANIFEST.csv` rewritten. Both values fed only results computed after convergence, so
  paths, choices and FleetPy did not change. A full run differed from the reference only in the evaluation file (34
  values: FRT and microtransit VMT and speed x 0.99978873, FRT and microtransit operating cost, subsidies and the
  ratios built on them; `tot_sub` 7781.65 -> 7781.42); the file was replaced, recorded in
  `docs/reference_results/README.md`, and a second full run printed `REPRODUCED`. The optimizer's subsidy objective
  for the reference candidate moves by the same amount (old sessions differ by up to about 0.02 %). A parameter file
  that still has one of the two keys stops with "unknown parameter".
- **Not fixed here (see I-31):** the FRT link distances may be miles x 1000, not metres (their sums are about 1.6 x
  shorter than the straight lines between the end stops). The FRT line length is computed from them, so it may be off
  by that factor, whichever meters-per-mile value is used.
- **Update 2026-11-25 (user's decision):** `meters_per_mile` set to the exact 1609.344 (the international mile) on
  `main`, with a reference update. A full run differed from the reference in 3 files: the evaluation file (55 values,
  both columns) and the two individual results files (every row: distances in miles; in the scenario also out-of-pocket
  costs, generalized cost saved, logsum increase and choice probabilities in the last digits). Nobody changed mode;
  FleetPy's inputs and results did not change; distances, fares, costs and the values built on them moved by at most about 0.0003 % (1609.344 / 1609.34 = 1.0000025):
  `tot_sub ($)` 7,796.0346 -> 7,796.0333, `tt_mob_lgsm_inc_with_micro` 913.2664 -> 913.2677, `M_revenue ($)`
  863.8903 -> 863.8888, `F_VMT (mi)` 2,354.0317 -> 2,354.0259. The 3 files were replaced by the run's; a second full
  run printed `REPRODUCED`. `mtsm_data/MANIFEST.csv` rewritten. Optimizer sessions before this change differ in the
  last digits.

### I-16: The aggregate convergence test is unfinished
- **Status:** Closed (2026-11-23). **Severity:** Low. **Found:** 2026-11-09 (restructuring the entry script, step 1).
- **What:** `run_examples_new_parking.py` has two convergence tests, chosen by `indiv_converg_test`. The run uses
  the individual-level test (`True`). The aggregate-level test (`False`, `convergence_test.convergence_test`)
  would compare only the microtransit mode share with the previous iteration. The user wants to keep it for
  later (2026-11-09), so it was kept and commented, not removed. It does not work as it is:
  - its call is commented out, and nothing computes `M_share` / `M_share_pre`, so `converged` never becomes True;
  - the stop at `maximum_iteration` is only in the individual-level branch, so the iteration loop would never end;
  - `convergence_test()` sets `converged` only when the test passes; when the share changed by more than 1% the
    `return` raises `UnboundLocalError`.
- **Impact:** none on results; `indiv_converg_test = True` is fixed in the code. Setting it to `False` would make
  the model loop forever.
- **Fix (when it is needed):** compute the microtransit mode share per iteration (`M_share`, and `M_share_pre`
  from the previous iteration), restore the call, move the `maximum_iteration` stop out of the individual branch so
  that it applies to both tests, and set `converged = False` at the start of `convergence_test()`. Then test it.
- **Checked 2026-11-23:** `indiv_converg_test` is `True` in every commit since the baseline `6d311ee` ("codebase as
  found"); no commit ever set it to `False`. The optimizer, `tools/` and the scripts in `standalone_scripts/` do not
  set it either (the four old entry scripts there have `True`). So the aggregate test was never used in any version
  in git.
- **Resolution:** user's decision: remove it (not finish it). Removed: `convergence_test()` in
  `mtsm_model/helpers/convergence_test.py`; the switch branch with the commented-out call in `mtsm_model/model.py`
  (the individual-level test now runs without the `if`; its lines unchanged, one level less indented); the parameter
  `indiv_converg_test` (line in `mtsm_constant_configurations.csv`, key and type in `mtsm_global_parameters.py`,
  `config.INDIV_CONVERG_TEST`); `mtsm_data/MANIFEST.csv` rewritten for the parameter file. A parameter file that
  still has the line now stops with "unknown parameter indiv_converg_test" (e.g. copies in the optimizer's
  `candidate_configs/` from earlier sessions; new candidates are copies of the frozen file). Full run:
  `compare_reference.py` printed `REPRODUCED` (32 identical).

### I-12: FleetPy's example a) serves 90 users; its check expects 88
- **Status:** Closed (2026-11-23). **Severity:** Low. **Found:** 2026-11-08 (removing downtown San Diego, step 1).
- **What:** `python run_examples.py` in `fleetpy/` runs example a) (`constant_config_ir.csv`, `example_ir_only.csv`)
  on the restored upstream data (Munich, 7,617 nodes, 5 vehicles). It serves 90 of 100 users; the check, unchanged
  since FleetPy's first release (2021-12-07), expects 88. The run otherwise completes normally.
- **Not the cause:** the vehicle capacity (the same 90 with upstream's capacity 4) and the example data (restored
  byte for byte).
- **Likely cause, not verified:** the environment. Upstream FleetPy was written for numpy 1.19 / pandas 1.2; the
  model's environment has numpy 2.2 / pandas 2.2, and four pandas-2 fixes in `src/`.
- **Impact:** none on the Lemon Grove results. It means FleetPy's own example cannot be used as a pass/fail check
  of FleetPy here.
- **Fix:** run upstream `7019960` unchanged in an environment with its original requirements: 88 there confirms
  the environment as the cause, and 90 can then be recorded as the expected value in this environment.
- **Checked 2026-11-23** (scripts and environments in the session scratchpad; nothing in the repo changed): example
  a) only, run by a small driver that calls the tree's own `run_examples.run_scenarios` and
  `read_outputs_for_comparison`; upstream `7019960` downloaded from GitHub as a zip.

  | code | environment | number users |
  |---|---|---|
  | ours (`fleetpy/`) | `fleetpy` (Python 3.10.19, numpy 2.2.6, pandas 2.2.3) | 90 |
  | ours | old: Python 3.8.20, numpy 1.19.5, pandas 1.2.0, networkx 2.3, scipy 1.5.4, pyproj 2.6.1.post1 (FleetPy's pins) | 90 |
  | upstream `7019960`, unchanged | old | 90 |
  | upstream `7019960`, unchanged | `fleetpy` | stops: `read_csv() got an unexpected keyword argument 'squeeze'` (the reason for the pandas-2 fixes) |

  - All three runs that finish give the same `standard_eval.csv` values to the last digit (served 90 %, shared
    rides 46.67 %, total vkm 212.3717404453077). `PYTHONHASHSEED` 0, 1, 2, 3, 12345 (ours, `fleetpy` env) and 0, 7
    (upstream, old env) change nothing.
  - Our `src/` differs from upstream only in the four pandas-2 files; `data/` and `studies/` are identical
    (`diff`, line endings ignored).
  - Upstream kept `"number users": 88` for example a) in later versions too (`1f736d3`, `ff372cb`, 2025); its
    `run_examples.py` was moved in 2026-03.
  - So the cause is not the environment and not the local changes: upstream's expected value does not match upstream's
    own code and data at `7019960` (the 88 may come from an earlier FleetPy version or another platform; not
    traced). 90 is the expected value of FleetPy `7019960` here.
  - Side note: upstream's evaluation fails with `FileNotFoundError` when the FleetPy folder sits in a deep path (the
    result file path then passes Windows' 260-character limit).
- **Resolution:** the "likely cause" above is ruled out; upstream's check value is stale. 90 is recorded as the
  expected value of example a) in `fleetpy/LOCAL_CHANGES.md`. `fleetpy/run_examples.py` keeps the 88 (user's
  choice: docs only, no change to FleetPy), so its mismatch message for 90 is the expected result. No model code
  changed; the Lemon Grove results are not affected.

### I-11: Old, unused MTSM files inside `fleetpy/`
- **Status:** Closed (2026-11-23). **Severity:** Low. **Found:** 2026-11-07 (comparison with upstream FleetPy).
- **What:** files added for MTSM that the current run does not read (updated 2026-11-08, after the downtown San
  Diego files were deleted): 69 old files in
  `fleetpy/data/demand/lemon_grove_example_demand/matched/lemon_grove_example_network/`, 9 Lemon Grove plots in
  `fleetpy/data/demand/example_demand/matched/example_network/`, and 13 old scenario configs of unknown study area
  (`example_ir_only_N_veh.csv`, `debug_example_ir_only*.csv`). Full list: `fleetpy/LOCAL_CHANGES.md`.
- **Impact:** none on results; `fleetpy/` is not yet only FleetPy.
- **Fix:** decided not to do it in the FleetPy separation (D4). Later: move them to an archive (or delete them; they
  stay in the git history), after checking that no script still needs them.
- **Checked 2026-11-23:** every tracked file in the repository was searched for the 91 file names. Only the 13
  configs (they name the old demand files `fleetpy_demand.csv` and `debug_fleetpy_demand.csv`) and old scripts in
  `standalone_scripts/` refer to them; nothing the model run, the optimizer or `tools/` uses. The run writes its own
  FleetPy config (`rq_file = lemon_grove_debug_False_fleetpy_demand.csv`). But the run also writes its FleetPy demand
  into the first folder and never created it: in a fresh clone the folder existed only because the old files were
  tracked in it.
- **Resolution:** the 91 files were removed with `git rm` (user's choice: delete, not archive; the last commit that
  has them is `91c7486`). `config.check_run_config` now also creates `mtsm.LG_FLEETPY_DEMAND_DIR` at the start of a
  run. `fleetpy/LOCAL_CHANGES.md` updated. Checked as in a fresh clone: with the whole
  `fleetpy/data/demand/lemon_grove_example_demand/` folder moved away, a full run recreated it and
  `compare_reference.py` printed `REPRODUCED` (32 identical). `standalone_scripts/` still names some of the files
  (left untouched on purpose).

### I-03: The optimizer has not been run since the changes
- **Status:** Closed (2026-11-13). **Severity:** Medium. **Found:** 2026-10-23 (Phases 1c and 2b).
- **What:** `Bayesian_optimization_script.py` was changed three times: the `mtsm_data/` paths (`d5aee47`), launching the model
  with `sys.executable` (`da839b0`), and stopping on a failed model run (`09e0684`). Each change compiles, and the
  failure handling was tested against a fake model process. The optimizer itself was never run, because a session
  takes many model evaluations, overwrote the parameter file (I-02, closed 2026-11-10) and needs Gurobi (I-01).
- **Impact:** an error in the optimizer's own code would only show up in the first real session.
- **Fix:** after I-01 is fixed, run a short session (a few candidates) into a throwaway `folder_name`. Check that
  `per_call_results.csv` matches the evaluation files and the copies in `candidate_configs/`, and that a
  deliberately failed run stops the optimizer.
- **Update 2026-11-12:** a short session was run (5 Sobol samples, 2 optimization iterations, throwaway folder, deleted
  afterwards): after the fix of I-27 it ran to the end; 7 model runs, one with headway 20, no rejected requests (Gurobi
  not started); `check_inputs.py` passes. Not yet checked: `per_call_results.csv` against the evaluation files and
  `candidate_configs/`, a deliberately failed run, and a candidate with rejected requests.
- **Update 2026-11-12 (second session, after I-28 and I-29):** again 5 Sobol samples and 2 optimization iterations
  into a throwaway folder (deleted afterwards): ran to the end in 37 min, 7 model runs (fleet 2-6, headway 12-29).
  Checked: every row of `per_call_results.csv` (objectives and a sample of metrics) equals the values in that
  candidate's saved evaluation file; no empty cells; the base case is the same in all 7 files (headway 20, `tot_sub`
  2320.67). Two candidates had rejected requests (9 % and 15 %), so AlonsoMora repositioning started Gurobi with the
  renewed license, and those runs finished. Afterwards a reference run: `REPRODUCED`, `check_inputs.py` passes.
  Still not checked: `per_call_results.csv` against the files in `candidate_configs/`, and a deliberately failed run.
- **Resolution (2026-11-13):** the two remaining checks were made; no code was changed.
  - *Candidate files:* a session with 3 Sobol samples into a throwaway folder (deleted afterwards). For the two
    candidates that ran, `config_call_0001.csv` and `config_call_0002.csv` differ from the frozen
    `mtsm_constant_configurations.csv` in exactly the 7 candidate values (7 of 55 lines; names, descriptions and CRLF
    unchanged), and these values are the ones in rows 1 and 2 of `per_call_results.csv`. The saved evaluation files
    show the candidates' headway (22, 12) and, as average FRT fare of the first, its transit fare.
  - *Failed run, real model:* the third candidate's file was given a text as fleet size (in the launcher's memory;
    the repo file was not edited). The model stopped with `fleet_size = 'not_a_number' is not a int`; the optimizer
    stopped one second later with exit code 1 and the message "the model run failed (exit code 1), for candidate
    [...]. ... Results of the earlier candidates: ...per_call_results.csv". `per_call_results.csv` kept the two good
    rows and got no row for the third. A second session, in which the first of three candidates failed, started no
    model run for the other two (exit code 1).
  - *The other failure checks, with a stand-in for the model* (the optimizer's own `run_script`, output folder in a
    scratch folder): exit code 3; no output files; no output files while complete files of an earlier candidate are
    lying there (they are deleted first); an evaluation file with the metric names only; one with an empty
    `FRT_only` column; one without the `FRT_and_micro` column. Each stopped with its own message; a complete
    evaluation file was accepted.
  - Afterwards a reference run: `REPRODUCED` (32 files); `check_inputs.py` passes.
  - Noticed, not changed: `per_call_results.csv` shows the candidate values with 7-8 digits (`3.8201945`), the
    candidate file has all digits (`3.8201944828033447`); they are the same single-precision number (relative
    difference up to 3e-8). The exact values of a candidate are in `candidate_configs/`. The stop message comes inside
    a long Ax traceback (Ax wraps the error); the model's own error line stands above it.

### I-29: Evaluation file: one line per metric, read by name by the optimizer
- **Status:** Closed (2026-11-12). **Severity:** Medium. **Found:** 2026-11-12 (user's request).
- **What:** `lemon_grove_evaluation_zonal_partition_False.csv` had one row per case and 75 columns, and the optimizer
  read it by position (`rows[2][30]`, "all columns except 0-9 and 72"). The columns `test_scen` (0 / 10) and
  `dscrptn` (`FRT_only_scen` / a fixed text) no longer said anything.
- **Resolution (user's decisions):**
  - The file has one line per metric and three columns: `metric_name`, `FRT_only` (base case), `FRT_and_micro` (the
    scenario); 74 lines. `test_scen` and `dscrptn` are gone, and with them the text
    `"Ritun BO (time-based+intrmdl_trfr+Micro_start+dist_based_fr)"`, which was set in `results.py`. The metric
    `microtrasnit` is now spelled `microtransit`. The other 72 metric names and their order are unchanged.
  - Model: `results.EvaluationTable` (new) holds the two columns and writes the file: at the start of the run with
    the metric names only, and again when a column is set. `model.run_model` no longer keeps the file open.
  - Optimizer: `read_evaluation_file()` and `evaluation_value()` read by column header and metric name; the two
    objectives are `tot_sub ($)` and `tt_mob_lgsm_inc_with_micro` of both columns; the 64 values for
    `per_call_results.csv` are read by the names in `METRIC_COLS`. A missing column, metric or value stops the
    optimizer with a message naming it (before: a check of the number of lines). `per_call_results.csv` keeps its
    layout; the `agg_sim_output_*.csv` copies have the new one.
  - Checked: a full run differed from the reference only in the evaluation file (31 of 32 identical). The new file,
    turned back into rows, equals the reference text for text, apart from the two removed columns and the corrected
    name. The optimizer's own `collect_output`, run on the new file, returns the same two objectives (-5460.99,
    903.05) and the same 64 metric values as the reading by position on the old file. The reference file was
    replaced; a second full run: 32 identical, `REPRODUCED`. No optimizer session was run.
- **Not changed:** the scripts in `standalone_scripts/` that read the old layout. Left open: I-30.

### I-04: Rows 1 and 2 of the evaluation CSV are identical
- **Status:** Closed (2026-11-12). **Severity:** Medium. **Found:** 2026-10-23 (Phase 1).
- **What:** `mtsm_data/lemon_grove/output/lemon_grove_evaluation_zonal_partition_False.csv` has 3 data rows. Rows 1 and 2
  are identical `FRT_only_scen` / `non_micro` rows (the fixed-route-only baseline). Row 3 is the microtransit scenario.
- **Impact:** none on the optimizer objectives, which come from row 3. The optimizer also reads values from row 2
  (`rows[2][...]`), so if the duplicate is a mistake, it matters which of the two rows is meant to be there.
- **Where (found 2026-11-09):** `run_examples_new_parking.py` writes the `FRT_only_scen` row twice in the same
  pass, both under `if test_scenario == TRPartA_test_scenario_list[0]`: once inside the block that writes the
  fixed-route-only individual results (line 1380), and once more right after that block (line 1427). The two
  `writerow` calls are not identical in their source, but give identical rows here (line numbers as of
  restructuring step 1, `docs/entry_script_refactor_plan.md`). Since step 7 both are in
  `mtsm_model/results.py`, `write_converged_results()` (lines 330 and 377).
- **To decide:** is the duplicate intended? If not, remove one of the two `writerow` calls.
  Any change to the file's rows also changes the optimizer's row indices and the reference results, so it needs a new
  reference.
- **Resolution (2026-11-12, user's decision):** the second of the two `writerow` calls was removed (I-28, second
  part): nothing needed two rows. Since I-29 the file has one column for the base case.

### I-28: The base case's subsidy used the FRT cost of the scenario's headway, not of the base headway
- **Status:** Closed (2026-11-12). **Severity:** High (it changes the optimizer's subsidy objective). **Found:**
  2026-11-12 (the user's question why a larger subsidy objective did not come with a larger logsum increase).
- **What:** the base case (FRT only, no microtransit) is defined by `base_frt_headway` (20 min) and `base_frt_fare`
  ($2.50): its travelers are routed on that network with that fare. But `results.py` computed its subsidy as
  `F_oper_cost - off_micro_F_revenue`, with `F_oper_cost` at the scenario's headway (`frt_headway`), although
  `F_oper_cost_base` existed and was printed in the same row. The base rows of the evaluation file also showed the
  scenario's headway in `hdwy (min)` and its FRT vehicle miles in `F_VMT (mi)`, `tt_VMT (mi)`, `F_PMT/F_VMT`.
- **Impact:** in the optimizer's subsidy objective (`tot_sub` of the microtransit row minus `tot_sub` of the base
  row) the FRT operating cost cancelled, so a shorter FRT headway cost nothing, while it raised the logsum increase
  (which is measured against the base headway). The objective was almost only fleet size x cost per vehicle (13 runs:
  correlation with fleet size 1.00, with the logsum increase 0.51).
- **Resolution (user's decision: the base case uses the base headway and base fare):** in `results.py` the base
  subsidy uses `F_oper_cost_base`; the base rows show `base_frt_headway` and the base headway's vehicle miles
  (`transit_tt_VMT_base`), also in `tt_VMT`, `F_PMT/F_VMT`, `sub_per_F_VMT`, `sub_per_T_VMT`; the fallback FRT waiting
  time for a base case without FRT trips uses the base headway. The fare was already right (`base_frt_fare` in the
  revenue and in the path search). Checked: a full seed-0 run differed from the reference in 1 of 32 files, the
  evaluation file, and there only in 13 columns of the two base rows, with the predicted values (`tot_sub` 4688.83 ->
  2320.67 = 2368.17 - 47.50); the microtransit row is identical. A run with `frt_headway` 30 gave the same base row
  except the two accessibility columns below. The reference was updated (`docs/reference_results/README.md`).
- **Effect on the optimizer:** no change to how it reads the results. The subsidy objective now includes the FRT cost
  difference to the base headway: -2368 at headway 10 (reference run: -3092.8 -> -5461.0), 0 at 20, +789 at 30.
  Results of earlier sessions are not comparable; they can be converted from the saved `agg_sim_output` files (new
  objective = old - (`F_oper_cost` of row 3 - `F_oper_cost` of row 2)). `ref_point` was widened from -15000 to
  -18000 (user's decision), because fleet 7 with headway 10 is now near -15,200.
- **Left as it is:** the base rows' `wghted_acc_emp_*` columns are still computed on the FRT network of the
  scenario's headway (`all_scenario_fixed_acc_calculation(headway, ...)`; they need the base headway's network and
  change a second output file, `debug_False_acc_super_network_non_micro_<headway>.csv`). The names of the base case's
  output files keep `hw_<scenario headway>`. The base row is still written twice (the optimizer reads rows 2 and 3).
- **Second part, 2026-11-12 (user's decision: do both; a second reference update the same day):**
  - *Accessibility of the base case:* `scenarios.py` calls `all_scenario_fixed_acc_calculation` with
    `config.BASE_FRT_HEADWAY`, and the function reads the frozen base network
    `initial_network/initial_super_network_non_micro_hw_20.csv` (the one the base travelers are routed on) instead of
    the scenario headway's copy in `initial_network_0719/`. Its output file is therefore now
    `debug_False_acc_super_network_non_micro_20.csv` for every run (was `..._non_micro_<scenario headway>.csv`).
    Checked: against the reference, only the base rows' `wghted_acc_emp_10_min` (583.20 -> 402.64) and
    `wghted_acc_emp_15_min` (1791.63 -> 1031.14) changed (`wghted_acc_emp_5_min` 107.60 is the same on both
    networks), plus the renamed file; the microtransit row is identical. A run with `frt_headway` 30 now gives
    exactly the reference's base row, and its microtransit row did not change.
  - *Base row written once:* `results.py` had the statement that writes the base row twice, back to back (the
    second a reformatted copy; already so in the baseline commit; no reader needed two rows). The second copy was
    removed. The evaluation file now has 3 lines: header, base case, microtransit scenario. The optimizer reads the
    file by position, so `collect_output` now reads rows 1 and 2 (were 2 and 3) and `run_script` requires 3 lines
    (was 4). `agg_sim_output_*.csv` files of earlier sessions keep the old layout. Checked: against the reference,
    the evaluation file is the reference's without its line 3, byte for byte; the optimizer's own `collect_output`,
    run on the new reference outputs, returns the objectives -5460.99 and 903.05, the values of before.
  - Still as it is: the names of the base case's other output files keep `hw_<scenario headway>`
    (`individual_results_non_micro_...`, `..._non_micro_..._transit_edges_rders_...`).
- **2026-11-24:** the accessibility calculation was removed (I-37), so the points above about the base rows'
  `wghted_acc_emp_*` columns and `debug_False_acc_super_network_non_micro_20.csv` no longer apply.

### I-27: The optimizer crashed at its first optimization iteration (numpy/MKL in the `fleetpy` env)
- **Status:** Closed (2026-11-12). **Severity:** High. **Found:** 2026-11-12 (first optimizer session since the changes:
  5 Sobol samples and 2 optimization iterations).
- **What:** in the `fleetpy` env, any LAPACK call of numpy or scipy (even `np.linalg.cholesky` of a 5x5 matrix) ends the
  process with the Windows exception `0xc06d007f` (exit code 127, no Python traceback): the Intel threading layer of MKL
  2024.2.2 asks `libiomp5md.dll` for a function that the one of `llvm-openmp` 21.1.3 does not have. Both packages are in
  the locked environment (`env/fleetpy.conda-explicit.txt`). The optimizer died after the Sobol samples, in the first
  Gaussian-process fit (`Models.BOTORCH_MODULAR` -> `scipy.optimize` L-BFGS-B).
- **Impact:** no optimizer session could get past the Sobol samples. The model is not affected: it never calls LAPACK
  (all runs and the reference were made in this env).
- **Resolution:** `Bayesian_optimization_script.py` sets `MKL_THREADING_LAYER=SEQUENTIAL` before numpy is imported
  (`os.environ.setdefault`; user's decision, option 1 of 3; the environment is unchanged). The model runs it starts
  inherit the variable. Checked 2026-11-12: with the variable, a session of 5 Sobol samples and 2 optimization
  iterations ran to the end (7 model runs, all result files written, `check_inputs.py` passes); a full seed-0 run with
  the variable set: `compare_reference.py` **32 identical, `REPRODUCED`**; after the change, the optimizer's
  Ax/BoTorch part (model runs replaced by fixed values) ran to the end without the variable set outside.
  Left open: the cause in the environment (another `llvm-openmp` build would remove it; that changes `env/`).

### I-01: Gurobi license expired
- **Status:** Closed (2026-11-12). **Severity:** High. **Found:** 2026-10-23 (Phase 2b, step 3).
- **What:** the academic Gurobi 12 license on the reference machine expired on 2026-10-21. Starting a Gurobi
  environment fails with `GurobiError: License expired 2026-10-21`.
- **Impact:** AlonsoMora repositioning starts Gurobi only after a request is rejected. The reference run has no
  rejections, so it still reproduces. Any parameter set with rejections, which includes most optimizer sessions,
  stops with the license error. Since commit `09e0684` the optimizer then stops too, instead of recording stale results.
- **Fix:** renew the academic license at gurobi.com and install it with `grbgetkey` (the user's action). Then run
  `python tools/export_env.py --write` to update `env/fleetpy.system.txt` with the new expiry date, and check that the
  three lock files are unchanged.
- **Resolution:** the user installed a new named-user academic license on 2026-11-12 (`TYPE=ACADEMIC`, `VERSION=14`,
  expires 2027-11-12; it works with the installed `gurobipy` 12.0.3). Checked: `gurobipy.Model()` starts in the
  `fleetpy` env; `python tools/export_env.py --write` changed only the license line of `env/fleetpy.system.txt`, the
  three lock files are unchanged. The license has to be requested again before 2027-11-12.

### I-26: A run with `--config` failed at once: the command line was handed to FleetPy
- **Status:** Closed (2026-11-11). **Severity:** High. **Found:** 2026-11-11 (a full run with the transfer penalty
  switched on through `--config`).
- **What:** `scenarios.scenarios()` still had a branch from FleetPy's example script: `if len(sys.argv) > 1:
  fleetpy.run_scenarios(*sys.argv)`, i.e. with any command-line argument, FleetPy was called with the arguments
  instead of running the scenario. Until 2026-11-10 the model was never started with arguments. Since config step 4
  (`docs/constant_config_plan.md`) `run_examples_new_parking.py --config <file>` exists, and FleetPy got `"--config"`
  as `n_parallel_sim`: `AssertionError: n_parallel_sim must be of type int`, before the first iteration.
- **Impact:** every run with `--config` failed, so every candidate of the optimizer, which starts each candidate with
  `--config` (from 2026-11-10 to 2026-11-11; the optimizer stops on the failed run, it records no stale results).
  Runs without arguments, the reference included, were not affected. Step 4 had checked the optimizer's file writer,
  not a run with `--config`.
- **Resolution:** the branch was removed (the scenario always runs; unused `import sys` removed). Checked with three
  full seed-0 runs: without `--config` under the I/O tracer `REPRODUCED`; with `--config` and a copy of the frozen
  file (the optimizer's way, "different from the frozen file: none") `REPRODUCED`, the same 32 files; with
  `--config` and the transfer penalty on: ran to the end (6:17), results differ as expected (I-25).

### I-23: After a microtransit leg, the discounted FRT fare was also charged on alighting
- **Status:** Closed (2026-11-11). **Severity:** Medium. **Found:** 2026-11-11 (checking the FRT <-> microtransit
  transfers).
- **What:** an FRT ride is boarding (walk node -> stop, link type 2, the fare), ride (type 1) and alighting
  (stop -> walk node, also type 2, no fare). In `network_algorithms.generalized_cost_dijsktra_OD_heap` the transfer
  discount `transit_fare = transit_fare_set * Micro2FixedFactor` was set for every type 2 link of a path that had
  used microtransit, also on the alighting link, so the discounted fare was charged twice.
- **Impact:** a microtransit -> FRT trip paid `2 x Micro2FixedFactor` times the FRT fare instead of `1 x` (at 0.5 the
  full fare; above 0.5 more than without discount). None in the reference run (`micro2fixed_factor` 0); the
  optimizer varies `micro2fixed_factor`, so its candidates with a factor above 0 had these trips priced wrong.
- **Resolution:** the two lines moved into the boarding branch (walk node -> stop); alighting stays at 0. Checked
  with both factors 0.5 on the final networks: the microtransit -> FRT paths pay 0.5 x the fare (1.0 x with two
  FRT boardings), traveler 11539 $1.81 instead of $3.62. Full seed-0 run `REPRODUCED`.

### I-20: The skim modules and their functions in `network_algorithms.py` are not used by the run
- **Status:** Closed (2026-11-11). **Severity:** Low. **Found:** 2026-11-09 (removing unused code from
  `network_algorithms.py`).
- **What:** `get_auto_skims.py` and `get_walk_transit_skims.py` (all-to-all shortest paths: skims) are not imported by
  a model run; only the standalone `run_examples_*` scripts in `standalone_scripts/New folder/` import them. Five
  functions of `network_algorithms.py` (since 2026-11-10 in `mtsm_model/helpers/`) exist only for them: `read_network`, `read_walking_network`,
  `read_network_dist`, `dijsktra_source_to_all`, `dijsktra_all_to_all`. They were left untouched in the cleanup of
  `network_algorithms.py` (user's decision), because the reference run does not execute them and could not check a
  change.
- **Impact:** none on results; unused code at the root of the repository, listed in the README as part of the model.
- **To decide:** keep them, move them (with the five functions) to `pre_process/` as preprocessing tools, or delete
  them (git keeps the history; the standalone `run_examples_*` scripts would then no longer import).
- **Resolution (user's decision: delete):** `get_auto_skims.py`, `get_walk_transit_skims.py` and the five
  functions were deleted (git keeps the history), and with them the imports `OrderedDict` and `collections`,
  which only these functions used. Class `Link` stays: `read_super_network` uses it. The four
  `standalone_scripts/New folder/run_examples_new*.py` import the two modules but never call them; their imports
  now fail (they were already broken: old `determine_folders` signature; `standalone_scripts/` left untouched).
  Full seed-0 run `REPRODUCED`.

### I-02: The optimizer overwrites the frozen parameter file
- **Status:** Closed (2026-11-10). **Severity:** Medium. **Found:** 2026-10-23 (Phase 1c).
- **What:** `Bayesian_optimization_script.py` writes each candidate's values into
  `mtsm_data/input_parameter/input_parameter.csv`, which is a frozen, checksummed input. After a session the file holds the
  last candidate's values.
- **Impact:** after an optimizer session, `tools/check_inputs.py` and the model's startup check report the file as
  changed, and `tools/compare_reference.py` does not print `REPRODUCED` until the reference values are restored (they
  are listed in `docs/reference_results/README.md`). Nothing records which parameters produced the files in
  `mtsm_data/lemon_grove/output/`.
- **Fix:** Phase 3. Give each run its own parameter file and output folder, and record the parameters in a
  `run_manifest.json`. Until then, restore the file with `git checkout mtsm_data/input_parameter/input_parameter.csv` after
  each optimizer session.
- **Resolution:** each candidate has its own parameter file (docs/constant_config_plan.md, step 4). The
  optimizer copies the frozen `mtsm_data/input_parameter/mtsm_constant_configurations.csv`, sets the candidate's
  seven values by parameter name, saves the copy as `<folder_name>/candidate_configs/config_call_NNNN.csv` and runs
  the model with `--config <copy>`; the model reports at startup which values differ from the frozen file. The
  frozen file is never changed, and each candidate's parameters are kept next to its results.
  `input_parameter.csv` was deleted. Checked: the old and the new optimizer writer on three candidates give the
  same value strings and the same `RunConfig` values and types; full seed-0 run `REPRODUCED`. Still for Phase 3:
  a `run_manifest.json` with more than the parameters, and separate output folders per run.

### I-15: Unused columns in `input_parameter.csv`; the optimizer writes it by column position
- **Status:** Closed (2026-11-10). **Severity:** Low. **Found:** 2026-11-08 (removing the TRPartA / BayesianOptimization /
  debug_mode branches).
- **What:** the code no longer branches on `BayesianOptimization`, `TRPartA` or `debug_mode_list` (only the values
  TRUE, TRUE, FALSE are supported; the startup check refuses others). Since 2026-11-09 the same holds for
  `TRPartA_test_scenario_list` (the fare scenario): the code has only fare scenario 10 (`config.FARE_SCENARIO`), and
  the startup check refuses other values. The four columns are still in
  `mtsm_data/input_parameter/input_parameter.csv`, because `Bayesian_optimization_script.py` writes the candidate's
  values by column position (`rows[1][5]` to `rows[1][13]`: fares, fleet size, peak factor, Micro2FixedFactor,
  headway). Removing columns 1-4 would shift those positions.
- **Impact:** none on results; the columns are misleading (they look like options but have only one valid value).
- **Fix (later, user's intention):** remove the four columns from the input file and make the optimizer write by
  column name instead of position; then remove them from the startup check. `input_parameter.csv` is a frozen
  input, so `MANIFEST.csv` must be regenerated and the change recorded in `docs/progress.md`. The optimizer change
  needs a test run of the optimizer (I-03).
- **Resolution:** `input_parameter.csv` was replaced by `mtsm_constant_configurations.csv`
  (docs/constant_config_plan.md), which has no `TRPartA`, `BayesianOptimization`, `debug_mode_list` or
  `TRPartA_test_scenario_list` (user's decision 3); the fare scenario is the parameter `fare_scenario`. The
  optimizer writes by parameter name. The startup check keeps `test_area` (only lemon_grove) and `fare_scenario`
  (only 10). `MANIFEST.csv` regenerated. Checked as for I-02.

### I-18: In later fare scenarios, every traveler gets the parking values of one traveler
- **Status:** Closed (2026-11-09). **Severity:** Medium. **Found:** 2026-11-09 (restructuring the entry script, step 5).
- **What:** the car path is computed only in the first fare scenario (`test_scenario ==
  TRPartA_test_scenario_list[0]`) and cached for the others (`paths.PathCache`). The same call also returns the
  traveler's parking duration and gas cost coefficient (`parking_dur`, `bt_c_gas`), which are not cached. In the
  other fare scenarios, every traveler's parking charge is therefore computed with the values of the last traveler of
  the first fare scenario.
- **Impact:** none on the current runs: `input_parameter.csv` has one row, so there is one fare scenario. A file with
  several rows (several fare scenarios in one run) would give wrong car costs, and so wrong mode choices, in all but
  the first scenario.
- **Where:** since restructuring step 6 the carried values are explicit: `paths.PathCache.last_parking_dur` /
  `last_bt_c_gas`, read in `iteration.run_iteration` when the car path comes from the cache.
- **Fix:** cache `parking_dur` and `bt_c_gas` with the car path (two fields of `paths.AutoPath`). This does not change
  the reference (one fare scenario); test it with a two-row parameter file.
- **Resolution:** the fare-scenario loop and the path cache were removed together with fare scenarios 0-9
  (`docs/progress.md`, "Only fare scenario 10"): every traveler's car path, and with it `parking_dur` and
  `bt_c_gas`, is computed in every iteration, so no value is carried over any more. Full run: `REPRODUCED`.

### I-09: The model's vehicle capacity is stored in FleetPy's vehicle file
- **Status:** Closed (2026-11-08). **Severity:** Medium. **Found:** 2026-11-07 (comparison with
  upstream FleetPy).
- **What:** `fleetpy/data/vehicles/default_vehtype.csv` has `maximum_passengers` 8; upstream FleetPy has 4. The Lemon
  Grove run uses this vehicle type (`default_vehtype:2` in the scenario configs), so a model parameter lives in
  FleetPy's data, unrecorded and unchecked. `low_range_vehtype.csv` has the same change (not used by the run).
- **Impact:** a FleetPy update or a clean FleetPy copy would silently change the vehicle capacity from 8 to 4.
- **Resolution:** the model has its own vehicle type, `lemon_grove_vehtype` (capacity 8, other values unchanged),
  in `mtsm_data/lemon_grove/fleetpy_inputs/data/vehicles/`; it is a frozen input (`MANIFEST.csv`) and is copied into
  `fleetpy/data/vehicles/` before each run. The 26 Lemon Grove scenario configs and `fleetpy_runner.create_config_files`
  use it. FleetPy's two vehicle files are back to upstream (capacity 4). The reference changed only in the vehicle-type
  name (4 FleetPy files, see `docs/reference_results/README.md`); the 9 reported results are byte-identical.

### I-10: FleetPy's example data was overwritten with downtown San Diego data
- **Status:** Closed (2026-11-08). **Severity:** Low. **Found:** 2026-11-07 (comparison with
  upstream FleetPy).
- **What:** the downtown San Diego configs use FleetPy's `example_network` and `example_demand`, so FleetPy's example
  network (Munich), demand, vehicle distribution, depots, charging stations, zone mapping and example configs were
  overwritten. The list is in `fleetpy/LOCAL_CHANGES.md`.
- **Impact:** FleetPy's own examples (`fleetpy/run_examples.py`) cannot be run as upstream intends, so FleetPy cannot
  be tested on its own. The Lemon Grove run reads none of these files.
- **Resolution:** done as part of removing downtown San Diego (`docs/progress.md`), which replaced D6: the 14
  files were restored from upstream `7019960` byte for byte, and the downtown versions were deleted instead of
  archived (tag `last-with-downtown-sd` marks the last commit with them). FleetPy's example a) runs on the restored
  data (see I-12). The Lemon Grove run still reproduces the reference.

### I-08: FleetPy's `README.md` still installs from `requirements.txt`
- **Status:** Closed (2026-11-07). **Severity:** Low. **Found:** 2026-10-23 (Phase 2b, step 2).
- **What:** FleetPy's `README.md` (in `fleetpy/` since 2026-11-07) still says `conda install --file requirements.txt`.
  There is no `requirements.txt` in `fleetpy/`, and the one at the repository root is only a comment pointing to
  `env/`, so this installs nothing.
- **Resolution:** the new root `README.md` describes the model and points to `env/README.md`; it says not to use
  `requirements.txt` or FleetPy's own install instructions. `fleetpy/LOCAL_CHANGES.md` already records that
  FleetPy's `requirements.txt` was replaced. FleetPy's README is left as upstream. Docs only, no run needed.

### I-07: `docs/progress.md` plan table is out of date
- **Status:** Closed (2026-11-07). **Severity:** Low. **Found:** 2026-11-07.
- **What:** the Phase 2 row said "Tag + push to do". The push is done (`65861ec` is on `origin/main`), and the user
  decided not to add a `v2-env-locked` tag for now. Step 6 of the Phase 2b plan also still mentioned the tag.
- **Resolution:** the row and step 6 were updated with the FleetPy separation docs (step 2). Docs only, no run needed.
