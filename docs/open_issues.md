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
| I-01 | Gurobi license expired | High | Open | 2026-10-23 |
| I-02 | The optimizer overwrites the frozen parameter file | Medium | Open | 2026-10-23 |
| I-03 | The optimizer has not been run since the changes | Medium | Open | 2026-10-23 |
| I-04 | Rows 1 and 2 of the evaluation CSV are identical | Medium | Decision needed | 2026-10-23 |
| I-05 | `FRT_headway = 20` overwrites a frozen network | Medium | Decision needed | 2026-10-23 |
| I-06 | Accessibility uses a hard-coded network for its node list | Medium | Open | 2026-10-23 |
| I-07 | `docs/progress.md` plan table is out of date | Low | Closed (2026-11-07) | 2026-11-07 |
| I-08 | FleetPy's `README.md` still installs from `requirements.txt` | Low | Closed (2026-11-07) | 2026-10-23 |
| I-09 | The model's vehicle capacity is stored in FleetPy's vehicle file | Medium | In progress | 2026-11-07 |
| I-10 | FleetPy's example data was overwritten with downtown San Diego data | Low | Closed (2026-11-08) | 2026-11-07 |
| I-11 | Old, unused MTSM files inside `fleetpy/` | Low | Open | 2026-11-07 |
| I-12 | FleetPy's example a) serves 90 users; its check expects 88 | Low | Open | 2026-11-08 |
| I-13 | The `micro_only` scenario uses the downtown San Diego node limit | Low | Open | 2026-11-08 |

---

## Open

### I-01: Gurobi license expired
- **Status:** Open. **Severity:** High. **Found:** 2026-10-23 (Phase 2b, step 3).
- **What:** the academic Gurobi 12 license on the reference machine expired on 2026-10-21. Starting a Gurobi
  environment fails with `GurobiError: License expired 2026-10-21`.
- **Impact:** AlonsoMora repositioning starts Gurobi only after a request is rejected. The reference run has no
  rejections, so it still reproduces. Any parameter set with rejections, which includes most optimizer sessions,
  stops with the license error. Since commit `09e0684` the optimizer then stops too, instead of recording stale results.
- **Fix:** renew the academic license at gurobi.com and install it with `grbgetkey` (the user's action). Then run
  `python tools/export_env.py --write` to update `env/fleetpy.system.txt` with the new expiry date, and check that the
  three lock files are unchanged.

### I-02: The optimizer overwrites the frozen parameter file
- **Status:** Open. **Severity:** Medium. **Found:** 2026-10-23 (Phase 1c).
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

### I-03: The optimizer has not been run since the changes
- **Status:** Open. **Severity:** Medium. **Found:** 2026-10-23 (Phases 1c and 2b).
- **What:** `Bayesian_optimization_script.py` was changed three times: the `mtsm_data/` paths (`d5aee47`), launching the model
  with `sys.executable` (`da839b0`), and stopping on a failed model run (`09e0684`). Each change compiles, and the
  failure handling was tested against a fake model process. The optimizer itself was never run, because a session
  takes many model evaluations, overwrites the parameter file (I-02) and needs Gurobi (I-01).
- **Impact:** an error in the optimizer's own code would only show up in the first real session.
- **Fix:** after I-01 is fixed, run a short session (a few candidates) into a throwaway `folder_name`. Check that
  `per_call_results.csv` matches the evaluation files, that a deliberately failed run stops the optimizer, and then
  restore the parameter file (I-02).

### I-04: Rows 1 and 2 of the evaluation CSV are identical
- **Status:** Decision needed. **Severity:** Medium. **Found:** 2026-10-23 (Phase 1).
- **What:** `mtsm_data/lemon_grove/output/lemon_grove_evaluation_zonal_partition_False.csv` has 3 data rows. Rows 1 and 2
  are identical `FRT_only_scen` / `non_micro` rows (the fixed-route-only baseline). Row 3 is the microtransit scenario.
- **Impact:** none on the optimizer objectives, which come from row 3. The optimizer also reads values from row 2
  (`rows[2][...]`), so if the duplicate is a mistake, it matters which of the two rows is meant to be there.
- **To decide:** is the duplicate intended? If not, find where the rows are written in `run_examples_new_parking.py`.
  Any change to the file's rows also changes the optimizer's row indices and the reference results, so it needs a new
  reference.

### I-05: `FRT_headway = 20` overwrites a frozen network
- **Status:** Decision needed. **Severity:** Medium. **Found:** 2026-10-23 (Phase 1b). This predates the
  reproducibility work.
- **What:** `update_initial_net_with_bayesian_headway()` (`pre_process/process_network.py`) writes
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

### I-09: The model's vehicle capacity is stored in FleetPy's vehicle file
- **Status:** In progress (FleetPy separation, step 3). **Severity:** Medium. **Found:** 2026-11-07 (comparison with
  upstream FleetPy).
- **What:** `fleetpy/data/vehicles/default_vehtype.csv` has `maximum_passengers` 8; upstream FleetPy has 4. The Lemon
  Grove run uses this vehicle type (`default_vehtype:2` in the scenario configs), so a model parameter lives in
  FleetPy's data, unrecorded and unchecked. `low_range_vehtype.csv` has the same change (not used by the run).
- **Impact:** a FleetPy update or a clean FleetPy copy would silently change the vehicle capacity from 8 to 4.
- **Fix (decided, D5):** a vehicle type of the model's own (for example `lemon_grove_vehtype`, capacity 8) in
  `mtsm_data/lemon_grove/fleetpy_inputs/`, copied in before each run and checksummed; the scenario configs use it; FleetPy's
  two files go back to upstream. Only the vehicle-type name changes in FleetPy's intermediate files, so the reference
  is updated for those; the 9 reported output files must stay byte-identical.

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
  the `micro` branch, then test it.

---

## Closed

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
