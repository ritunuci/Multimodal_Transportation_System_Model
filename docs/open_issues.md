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
| I-03 | The optimizer has not been run since the changes | Medium | Open | 2026-10-23 |
| I-04 | Rows 1 and 2 of the evaluation CSV are identical | Medium | Closed (2026-11-12) | 2026-10-23 |
| I-05 | `FRT_headway = 20` overwrites a frozen network | Medium | Decision needed | 2026-10-23 |
| I-06 | Accessibility uses a hard-coded network for its node list | Medium | Open | 2026-10-23 |
| I-07 | `docs/progress.md` plan table is out of date | Low | Closed (2026-11-07) | 2026-11-07 |
| I-08 | FleetPy's `README.md` still installs from `requirements.txt` | Low | Closed (2026-11-07) | 2026-10-23 |
| I-09 | The model's vehicle capacity is stored in FleetPy's vehicle file | Medium | Closed (2026-11-08) | 2026-11-07 |
| I-10 | FleetPy's example data was overwritten with downtown San Diego data | Low | Closed (2026-11-08) | 2026-11-07 |
| I-11 | Old, unused MTSM files inside `fleetpy/` | Low | Open | 2026-11-07 |
| I-12 | FleetPy's example a) serves 90 users; its check expects 88 | Low | Open | 2026-11-08 |
| I-13 | The `micro_only` scenario uses the downtown San Diego node limit | Low | Open | 2026-11-08 |
| I-14 | The preprocessing code still contains downtown San Diego | Low | Open | 2026-11-08 |
| I-15 | Unused columns in `input_parameter.csv`; the optimizer writes it by column position | Low | Closed (2026-11-10) | 2026-11-08 |
| I-16 | The aggregate convergence test is unfinished | Low | Open | 2026-11-09 |
| I-17 | Travelers who keep their transit choice resubmit only their last microtransit and FRT leg | Medium | Open | 2026-11-09 |
| I-18 | In later fare scenarios, every traveler gets the parking values of one traveler | Medium | Closed (2026-11-09) | 2026-11-09 |
| I-19 | The microtransit start fare always gets the FRT-to-microtransit transfer discount | Low | Open | 2026-11-09 |
| I-20 | The skim modules and their functions in `network_algorithms.py` are not used by the run | Low | Closed (2026-11-11) | 2026-11-09 |
| I-21 | Three different meters-per-mile values (1609.34, 1609, 1.609 km) | Low | Open | 2026-11-10 |
| I-22 | The path search can miss the least-cost path when a transfer discount applies | Medium | Open | 2026-11-11 |
| I-23 | After a microtransit leg, the discounted FRT fare was also charged on alighting | Medium | Closed (2026-11-11) | 2026-11-11 |
| I-24 | Transfer fare rules: the discount lasts for the whole trip; re-boarding after microtransit is charged | Low | Open (to decide) | 2026-11-11 |
| I-25 | Turn on the transfer penalty (`enable_num_transfer_penalty`) with a new reference | Medium | Open (reminder) | 2026-11-11 |
| I-26 | A run with `--config` failed at once: the command line was handed to FleetPy | High | Closed (2026-11-11) | 2026-11-11 |
| I-27 | The optimizer crashed at its first optimization iteration (numpy/MKL in the `fleetpy` env) | High | Closed (2026-11-12) | 2026-11-12 |
| I-28 | The base case's subsidy used the FRT cost of the scenario's headway, not of the base headway | High | Closed (2026-11-12) | 2026-11-12 |
| I-29 | Evaluation file: one line per metric, read by name by the optimizer | Medium | Closed (2026-11-12) | 2026-11-12 |
| I-30 | The evaluation file holds one scenario; its base column is empty for runs without a base case | Medium | Open | 2026-11-12 |

---

## Open

### I-03: The optimizer has not been run since the changes
- **Status:** Open. **Severity:** Medium. **Found:** 2026-10-23 (Phases 1c and 2b).
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

### I-05: `FRT_headway = 20` overwrites a frozen network
- **Status:** Decision needed. **Severity:** Medium. **Found:** 2026-10-23 (Phase 1b). This predates the
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

### I-06: Accessibility uses a hard-coded network for its node list
- **Status:** Open. **Severity:** Medium. **Found:** 2026-10-23 (Phase 4 check).
- **What:** `create_nodes_emp_dict()` (`output_performance_metrics.py`) hard-codes `headway = 20` and `virstop = 100`
  and reads `mtsm_data/lemon_grove/initial_network_0719/initial_super_network_micro_hw_20_virstop_100.csv`, only to collect
  the set of node IDs. Nodes with no assigned employment get 0. The result feeds the `wghted_acc_emp_{5,10,15}_min`
  columns.
- **Impact:** none today. The file has the same 2269 nodes as the network the scenario uses
  (`initial_super_network_micro_hw_10_virstop_75.csv`). A future scenario with a different node set would get
  silently wrong accessibility numbers.
- **Fix:** take the node list from the network the scenario actually uses. If the node set is unchanged, the reference
  still reproduces; check with a full run and `compare_reference.py`.

### I-11: Old, unused MTSM files inside `fleetpy/`
- **Status:** Open. **Severity:** Low. **Found:** 2026-11-07 (comparison with upstream FleetPy).
- **What:** files added for MTSM that the current run does not read (updated 2026-11-08, after the downtown San
  Diego files were deleted): 69 old files in
  `fleetpy/data/demand/lemon_grove_example_demand/matched/lemon_grove_example_network/`, 9 Lemon Grove plots in
  `fleetpy/data/demand/example_demand/matched/example_network/`, and 13 old scenario configs of unknown study area
  (`example_ir_only_N_veh.csv`, `debug_example_ir_only*.csv`). Full list: `fleetpy/LOCAL_CHANGES.md`.
- **Impact:** none on results; `fleetpy/` is not yet only FleetPy.
- **Fix:** decided not to do it in the FleetPy separation (D4). Later: move them to an archive (or delete them; they
  stay in the git history), after checking that no script still needs them.

### I-12: FleetPy's example a) serves 90 users; its check expects 88
- **Status:** Open. **Severity:** Low. **Found:** 2026-11-08 (removing downtown San Diego, step 1).
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

### I-13: The `micro_only` scenario uses the downtown San Diego node limit
- **Status:** Open. **Severity:** Low. **Found:** 2026-11-08 (removing downtown San Diego, step 2).
- **What:** in `update_network_files.update_network_files`, the `micro_only` branch sets the microtransit waiting
  time only on waiting links with `from_node <= 731`, the last walk node of the downtown San Diego network, and
  without a study-area check. The `micro` branch uses `from_node <= 1098` for Lemon Grove.
- **Impact:** none on the current results: the run only uses `microtransit_running_scenarios = ["micro"]`. A
  Lemon Grove `micro_only` run would leave the waiting time of walk nodes 732-1098 at their initial values.
- **Fix:** decided to leave it for now (2026-11-08). If `micro_only` is needed: use the same Lemon Grove check as
  the `micro` branch, then test it. The user decided on 2026-11-09 to keep `micro_only` and `non_micro` as
  options in the restructuring (`docs/entry_script_refactor_plan.md`).

### I-14: The preprocessing code still contains downtown San Diego
- **Status:** Open. **Severity:** Low. **Found:** 2026-11-08 (removing downtown San Diego, step 2b).
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

### I-16: The aggregate convergence test is unfinished
- **Status:** Open. **Severity:** Low. **Found:** 2026-11-09 (restructuring the entry script, step 1).
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

### I-17: Travelers who keep their transit choice resubmit only their last microtransit and FRT leg
- **Status:** Open. **Severity:** Medium. **Found:** 2026-11-09 (restructuring the entry script, step 4).
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


### I-19: The microtransit start fare always gets the FRT-to-microtransit transfer discount
- **Status:** Open. **Severity:** Low. **Found:** 2026-11-09 (dropping fare scenarios 0-9).
- **What:** in the fare structure (the former fare scenario 10, `network_algorithms.generalized_cost_dijsktra_OD_heap`),
  the microtransit distance fare is multiplied by `Fixed2MicroFactor` only after an FRT trip leg (`IsFixedLink`),
  but the start fare at a microtransit waiting link is always multiplied by `Fixed2MicroFactor` (and by the peak
  factor), also when no FRT leg came before.
- **Impact:** none in the reference run (`Fixed2MicroFactor = 1`). When the optimizer sets `Fixed2MicroFactor` below
  1, every microtransit trip gets the transfer discount on its start fare, not only trips after FRT.
- **To decide:** is this intended? If not, apply the factor to the start fare only after an FRT leg, like the
  distance fare. This changes results for `Fixed2MicroFactor != 1` (not the reference).

### I-21: Three different meters-per-mile values (1609.34, 1609, 1.609 km)
- **Status:** Open. **Severity:** Low. **Found:** 2026-11-10 (one parameter file, `docs/constant_config_plan.md`).
- **What:** the code converts miles with three different values, now three parameters in
  `mtsm_constant_configurations.csv`: `meters_per_mile` 1609.34 (fares, gas costs, VMT; `config.MILE_METER`),
  `meters_per_mile_frt_lines` 1609 (FRT line lengths, `output_performance_metrics.get_transit_line_dist`) and
  `km_per_mile_fleetpy` 1.609 (FleetPy's vkm and km/h, `output_performance_metrics.get_fleetpy_eval_output_metrics`).
  They were kept apart so that the results stayed identical (user's decision 2: separate keys now, merge later).
- **Impact:** small differences in the FRT line durations and operating costs and in the microtransit VMT and speed
  reported from FleetPy (1609 vs 1609.34: about 0.02 %).
- **Fix (later, user's intention):** use one value (`meters_per_mile`, 1.60934 km) everywhere and remove the two other
  keys. This changes results: make and document a new reference in `docs/reference_results/`.

### I-22: The path search can miss the least-cost path when a transfer discount applies
- **Status:** Open. **Severity:** Medium. **Found:** 2026-11-11 (checking the FRT <-> microtransit transfers).
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

### I-24: Transfer fare rules: the discount lasts for the whole trip; re-boarding after microtransit is charged
- **Status:** Open (to decide). **Severity:** Low. **Found:** 2026-11-11 (checking the FRT <-> microtransit transfers).
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

### I-25: Turn on the transfer penalty (`enable_num_transfer_penalty`) with a new reference
- **Status:** Open (reminder: turn the switch on later; user's decision 2026-11-11). **Severity:** Medium.
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

---

## Closed

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
