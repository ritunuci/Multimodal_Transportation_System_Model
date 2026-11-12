# Reproducibility work: progress log

Goal: make the results we report for the research reproducible, and make the codebase self-contained (no
dependency on any folder outside `FleetPy_SanDiego`). Study area: **Lemon Grove only**.
Reported results: `mtsm_data/lemon_grove/output/`. Before 2026-10-23 they were written to
`D:\Ritun\Siwei_Micro_Transit\Bayesian_Optimization\lemon_grove\output_folder\`.
Entry point: `run_examples_new_parking.py`, run in the `fleetpy` conda env
(`C:\Users\Autonomicity\.conda\envs\fleetpy`, Python 3.10.19).

Newest entries go at the bottom of each phase. In the "Baseline findings" section, paths are relative to
`D:\Ritun\Siwei_Micro_Transit\` (the locations before `mtsm_data/`). Elsewhere they are relative to the codebase root.

Names: on 2026-11-07 the data folder `mtsm/` was renamed to `mtsm_data/` and the optimizer
`test_file_backup_latest.py` to `Bayesian_optimization_script.py`. This log uses the new names throughout, also for
earlier entries; commits before that date use the old names.

---

## Plan overview

| Phase | What | Status |
|---|---|---|
| 1 | Make a single run deterministic: seed, hash seed, PYTHONPATH, Gurobi check | Done, verified 2026-10-23 |
| 1b | Self-contained codebase: frozen, checksummed inputs and all outputs under `mtsm_data/` (former step 2.3); reference results; guard for unsupported configurations | Done, verified 2026-10-23 |
| 1c | Optimizer (`Bayesian_optimization_script.py`) reads and writes `mtsm_data/` instead of outside folders | Done 2026-10-23 (compiled, not run) |
| 2 | Freeze code (git: two-step commit, then GitHub repo) and environment (conda export, lock files) | Done 2026-10-23 and pushed (`65861ec`): git (Phase 2a); stale paths, env lock, rebuild test passed (Phase 2b). No `v2` tag (user's decision) |
| 2c | FleetPy as a separate module: `fleetpy/`, `fleetpy_runner.py`, inputs copied from `mtsm_data/` | Done 2026-11-08 (open: I-11, I-12) |
| 2d | Remove downtown San Diego: code (also commented), inputs and outputs | Done 2026-11-08 (left by decision: I-13, I-14) |
| 2e | Remove the `TRPartA`, `BayesianOptimization` and `debug_mode` branches (columns kept in the input file) | Done 2026-11-09 (open: I-15) |
| 2f | Restructure the entry script into a package (`docs/entry_script_refactor_plan.md`) | Done 2026-11-09 (open: I-16, I-17) |
| 2g | Only fare scenario 10: drop fare scenarios 0-9, the fare-scenario loop and the path cache (column kept) | Done 2026-11-09 (open: I-15, I-19) |
| 2h | Remove unused code from `network_algorithms.py` (skim functions left untouched) | Done 2026-11-09 (open: I-20) |
| 2i | Faster least-cost path search (`docs/path_search_speedup_plan.md`): run 18 -> 7 min | Done 2026-11-10 |
| 2j | Reuse the car and FRT paths across iterations: run 7 -> 5 min | Done 2026-11-10 |
| 2k | Move the helper modules from the root to `mtsm_model/helpers/` | Done 2026-11-10 |
| 2l | One parameter file `mtsm_constant_configurations.csv` (replaces `input_parameter.csv` and the values in the code) | Done 2026-11-10 |
| 2m | Delete the unused skim scripts and their five functions in `network_algorithms.py` (I-20) | Done 2026-11-11 |
| 2n | Transfers FRT <-> microtransit checked: discounted FRT fare no longer charged on alighting (I-23) | Done 2026-11-11 (open: I-22, I-24) |
| 2o | Transfer penalty `bt_f_trfer` per transfer behind a switch (off); link type 3 removed | Done 2026-11-11 (open: I-25) |
| 2p | Runs with `--config` (the optimizer's candidates) work again: FleetPy no longer gets the command line (I-26) | Done 2026-11-11 |
| 2q | Representative super-network script `pre_process/build_super_network.py` (not used by the model yet) | Done 2026-11-11 |
| 2r | Optimizer runs again: MKL threading set to sequential in `Bayesian_optimization_script.py` (I-27) | Done 2026-11-12 (open: I-03) |
| 2s | Base case's subsidy at the base FRT headway (I-28); reference updated (evaluation file) | Done 2026-11-12 |
| 3 | Per-run provenance: `run_manifest.json`, one output folder per run, guard against two runs at once | To do |
| 4 | Check the results before reporting them (see "Open questions") | To do |
| 5 | Regression test against reference outputs (tool and reference done in 1b); reproduce on a second machine | Partly done |
| 6 | Report the spread over several seeds; use common seeds for optimization candidates | To do |

---

## Baseline findings (2026-10-22/23)

### How a run behaves
- A run takes about 30 min and converges at iteration 5 for the current `input_parameter.csv` (lemon_grove, fleet 2, headway 10, scenario 10).
- Every run rebuilds its networks from the `base_*` files. Nothing is read before the same run writes it, so no state carries over between runs.
- The script and FleetPy run in one process (`n_parallel_sim=1`).
- The optimizer is **`Bayesian_optimization_script.py`** (codebase root). `New folder/MOBO_for_micro.py` is an older
  variant, kept but not used. The optimizer launches the run with `subprocess.run([fleetpy python, script])`. It edits
  `input_parameter.csv` **by column index** (5–13) and reads the evaluation CSV by index (`rows[3][30]`, `rows[3][50]`,
  `rows[2][...]`, all of row 3 except indices 0–9 and 72). So new columns must be appended at the end of
  `input_parameter.csv`, and the evaluation CSV's columns must not change. (Corrected 2026-10-23: earlier entries
  wrongly named `MOBO_for_micro.py` as the optimizer.)

### Files read (inputs), from an I/O trace of a full run
- `Bayesian_Optimization\Input_parameter\input_parameter.csv`
- `Bayesian_Optimization\demand_data\lemon_grove\lemon_grove_trips_nodes_study_area_with_beta.csv`
- `Bayesian_Optimization\lemon_grove\initial_network_folder\initial_network\`: `auto_edges.csv`,
  `base_super_network_lemon_grove_micro_hw_10_virstop_75.csv`, `base_super_network_lemon_grove_non_micro_hw_10.csv`,
  `initial_super_network_non_micro_hw_20.csv`
- `Data\0719_input\`: `pre_nodes.csv`, `final_land_use.csv`, `activitysim_output\lemon_grove_mgra_pop_inc.csv`,
  `activitysim_output\lemon_grove_mgra_adj.csv`, `lemon_grove\initial_network\initial_super_network_micro_hw_20_virstop_100.csv`
- `Ritun\lemon grove\`: `super_network_transit_edges.csv`, `network_folder\pre_nodes.csv`, `mgra_node_mapping\nodes_mgra_mapping.csv`
- `FleetPy_SanDiego\studies\example_study\scenarios\`: `lemon_grove_constant_config_ir_repo.csv`,
  `lemon_grove_example_ir_heuristics_repositioning_2_veh.csv`
- `FleetPy_SanDiego\data\`: `networks\lemon_grove_example_network\base\{nodes.csv, edges.csv, crs.info}`,
  `vehicles\{default_vehtype.csv, low_range_vehtype.csv}`,
  `fleetctrl\initial_vehicle_distribution\lemon_grove_example_network\imbalanced.csv`

### Files written (outputs)
- **Reported results:** `Bayesian_Optimization\lemon_grove\output_folder\`. This holds
  `lemon_grove_evaluation_zonal_partition_False.csv`, `individual_results_{micro,non_micro}_M_…_scen_10.csv`,
  `debug_False_acc_super_network_*.csv` and `debug_False_lemon_grove_{micro,non_micro}_…_transit_edges_rders_scen_10.csv`.
- **Intermediate files** (rewritten every iteration):
  - `Bayesian_Optimization\lemon_grove\final_network_folder\final_super_network_micro_…_{AM,MD,PM,EV}_….csv`
  - `Bayesian_Optimization\lemon_grove\initial_network_folder\initial_network\initial_super_network_{micro_hw_10_virstop_75,non_micro_hw_10}.csv`
  - `FleetPy_SanDiego\data\demand\lemon_grove_example_demand\matched\lemon_grove_example_network\{lemon_grove_debug_False_fleetpy_demand.csv, debug_False_F_transit_demand_….csv}`
  - `FleetPy_SanDiego\studies\example_study\results\example_pool_repo_AM_sc_1\*`, which FleetPy empties before each simulation
- **Other:** `Data\0719_input\indiv_output_folder\iter_{n}_1_user-stats.csv`,
  `Data\0719_input\lemon_grove\initial_network\initial_super_network_*_hw_10*.csv`, `FleetPy_SanDiego\standard_bugfix.log`

### Why results changed from run to run
1. **Main cause (confirmed):** the mode choice draws `random.random()` per agent, and the script never seeded `random`.
   FleetPy re-seeds `random`/`np.random` with `random_seed` (0, from the constant config) at the start of each simulation, so iterations 1 and later were
   seeded by accident. Iteration 0 was not, and its draws carried through to the final results.
   - The values differ between seeds. See the seed table under Phase 1 → Verification.
   - Two runs with `random.seed(42)`, `np.random.seed(42)` and `PYTHONHASHSEED=0` were **byte-identical on every file in
     `output_folder\`**. Only `00_simulation.log` and the timing column of `3-0_op-dyn_atts.csv` differed.
2. **Possible cause:** `network_algorithms.read_network` keeps text node IDs in a `set`. String hashing changes per process, so
   Dijkstra could break ties between equal-cost paths differently. This is fixed by `PYTHONHASHSEED=0`. (The super-network uses integer IDs, which hash the same way in every process.)
3. **Possible cause:** AlonsoMora repositioning calls Gurobi 12.0.3 with `TimeLimit=120` s
   (`src/fleetctrl/repositioning/AlonsoMoraRepositioning.py:130`). A solve that hits the limit on a slower machine skips
   repositioning. The baseline run had no such solves.
4. **Environment:** `PYTHONPATH` contains `C:/Users/Danny/PhD_Thesis_Project_27` (which doesn't exist) and SUMO's tools folder.
   They could shadow modules.

### Harmless noise
- The `[WinError 32] ... 00_simulation.log` messages come from FleetPy's log file still being open from the previous iteration,
  so it can't be deleted and keeps growing. Result files are not affected.

---

## Phase 1: make a single run deterministic

### Changes (2026-10-23)
- `run_examples_new_parking.py`:
  - **Relaunch guard** at the top of `__main__`: if `PYTHONHASHSEED != "0"`, the script relaunches itself with
    `PYTHONHASHSEED=0` and without `PYTHONPATH`, then exits with the child's exit code. This works for runs from the IDE, the terminal
    and the optimizer's subprocess.
  - **Seed:** reads `random_seed` from `input_parameter.csv` (defaults to `0` if the column is missing), calls
    `random.seed` and `np.random.seed`, and prints the seed.
  - **One seed for everything:** `run_scenarios(..., random_seed=...)` overrides FleetPy's `random_seed` from the constant
    config, so a single number controls the mode-choice draws and the simulation.
  - **Gurobi check:** `warn_non_optimal_repositioning()` runs after each FleetPy run and prints a red warning if any
    `70_repo_am_opt_model_infeasible_*.lp` files exist. AlonsoMora writes one whenever Gurobi does not reach an optimal solution, including when it hits the time limit.
- `Bayesian_Optimization\Input_parameter\input_parameter.csv`: added `random_seed` as the **last** column, value `0`.
  The original is saved as `input_parameter.csv.bak_before_seed` in the same folder. The optimizer keeps the extra column when it rewrites the file.

### Effect on results
- FleetPy's seed was already 0, so iterations 1 and later use the same seed as before. Iteration 0 is now seeded too, so
  results will differ from earlier unseeded runs. The earlier runs were themselves one random draw, so this doesn't make
  them wrong, but numbers from before and after this change are not comparable.

### Verification (2026-10-23): passed
- Two runs (C, D) with the new code, launched like the optimizer does (plain `fleetpy` python, inherited
  `PYTHONPATH`, no `PYTHONHASHSEED`). Both logged `random_seed: 0 PYTHONHASHSEED: 0`, so the relaunch works. Each took about 30 min and
  converged at iteration 5. No Gurobi warnings.
- **33 of 35 output files were byte-identical, including every file in `output_folder\`.** The only differences were
  `00_simulation.log` (timestamps) and the timing column of `3-0_op-dyn_atts.csv`. Neither is a result.
- The evaluation CSV has 3 data rows. Rows 1–2 are the fixed-route-only baseline (`FRT_only_scen`, `non_micro`).
  Row 3 is the microtransit scenario, and it is the row the optimizer reads (`rows[3]`).
- Row 3 (microtransit scenario), same input parameters, different seeds:

| Metric | unseeded | seed 42 (A = B) | **seed 0 (C = D), reference** |
|---|---|---|---|
| `tot_sub ($)` (optimizer objective 1) | 7579.70 | 7793.54 | **7781.654254** |
| `tt_mob_lgsm_inc_with_micro` (optimizer objective 2) | 857.47 | 1008.29 | **903.047435** |
| car mode share | 0.91395 | 0.920363 | 0.920363 |
| `M_trips` / `F_trips` | 77 / 26 | 66 / 23 | 68 / 22 |
| `M_avg_wait_time (s)` | 229.9 | 171.0 | 209.4 |
| `M_VMT (mi)` | 165.8 | 136.7 | 136.9 |

- Same seed gives identical values. A different seed moves objective 2 by up to about ±8% and objective 1 by about ±1.5% with
  nothing else changed. This is why Phase 6 matters, especially for the optimizer.

---

## Phase 1b: self-contained codebase (`mtsm_data/`)

### Layout (2026-10-23)
Each folder outside the codebase that the run used now has exactly one folder in `mtsm_data/`. No folder was split and no
file was renamed, so the code still builds the same file names. The folder constants are in `mtsm_paths.py`
(imported as `mtsm`). They are derived from the location of that file, so the codebase still works if it is moved.

| `mtsm_data/` folder | Former location (under `D:\Ritun\Siwei_Micro_Transit\`) | Contents |
|---|---|---|
| `input_parameter/` | `Bayesian_Optimization\Input_parameter` | `input_parameter.csv` (frozen input) |
| `region/` | `Data\0719_input` | `pre_nodes.csv`, `final_land_use.csv` (frozen) |
| `region/activitysim_output/` | `Data\0719_input\ActivitySim_output` | `lemon_grove_MGRA_pop_inc.csv`, `lemon_grove_MGRA_adj.csv` (frozen) |
| `lemon_grove/demand_data/` | `Bayesian_Optimization\demand_data\lemon_grove` | agent demand (frozen) |
| `lemon_grove/initial_network/` | `Bayesian_Optimization\lemon_grove\initial_network_folder\initial_network` | 4 frozen inputs plus 2 networks rebuilt each run |
| `lemon_grove/initial_network_0719/` | `Data\0719_input\lemon_grove\initial_network` | `..._hw_20_virstop_100.csv` (frozen) plus copies of the rebuilt networks, which the metrics code reads back |
| `lemon_grove/transit/` (+ `network_folder/`, `mgra_node_mapping/`) | `Ritun\Lemon Grove` (+ `Network_folder`, `MGRA_Node_Mapping`) | transit edges, road nodes, node→MGRA mapping (frozen) |
| `lemon_grove/final_network/` | `Bayesian_Optimization\lemon_grove\final_network_folder` | generated each iteration |
| `lemon_grove/indiv_output/` | `Data\0719_input\indiv_output_folder` | generated each iteration |
| `lemon_grove/output/` | `Bayesian_Optimization\lemon_grove\output_folder` | **reported results** |

- **Frozen inputs:** 14 files, copied unchanged. `mtsm_data/MANIFEST.csv` holds path, size, SHA-256 and role.
  `python tools/check_inputs.py` verifies them; `--write` regenerates the manifest. Only regenerate it after a deliberate
  input change, and record that change here.
- **FleetPy's own folders stay where FleetPy expects them:** `data/` and `studies/`. They were already inside the codebase, and are now
  referenced through `mtsm_paths` (`LG_FLEETPY_DEMAND_DIR`, `FLEETPY_RESULTS_DIR`) instead of absolute `D:/` paths.
- The old folders outside the codebase were **not modified or deleted**. The code no longer reads or writes them.

### Code changes (2026-10-23)
- `mtsm_paths.py`: new. All folder constants, derived from its own location.
- Rewired to `mtsm_paths`: only folder strings that a run actually uses, found with an I/O trace that recorded the
  calling line of every file access outside the codebase.
  - `folder_directory.py`: the lemon_grove branch of `TRPartA` + `BayesianOptimization` returns the `mtsm` folders.
  - `pre_process/process_network.py`: `update_initial_net_with_bayesian_headway()`, lemon_grove branch.
  - `output_performance_metrics.py`: module-level `network_folder` and `asim_output_folder`;
    `create_nodes_emp_dict()`, `accessibility_calculation()`, `all_scenario_fixed_acc_calculation()`,
    `get_fleetpy_eval_output_metrics()`, `get_transit_line_dist()`, `get_transit_link_info()`,
    `write_fixed_transit_link_vmt()` (lemon_grove / `TRPartA` + `BayesianOptimization` branches).
  - `update_network_files.py`: `copy_csv()` (user-stats copies), FleetPy results folder, initial and final network folders.
  - `get_microtransit_skims.py`: `get_node_ct()`, lemon_grove branch.
  - `run_examples_new_parking.py`: input-parameter folder, FleetPy results folder, and `standard_bugfix.log`, which now always
    goes to the codebase root instead of the current working directory.
- `run_examples_new_parking.py`, new startup block:
  - **Configuration guard.** The run stops with an error unless every `test_area` is `lemon_grove`, `TRPartA` and
    `BayesianOptimization` are TRUE, and `debug_mode_list` is FALSE. Other configurations still point to folders outside the
    codebase. `zonal_partition` is hard-coded to `False` in the script, so it can't be selected.
  - **Frozen-input check.** Prints a red warning (the run continues) if `check_inputs()` finds a missing or changed input.
  - **Output folders** in `mtsm_data/` are created if missing, since git does not keep empty folders.
- Not changed: absolute paths on branches the guard blocks (downtown_sd, `TR_PartA`, non-optimizer, zonal, debug), and unused
  variables on the active branches, such as `demand_folder` in `update_network_files.py` and `network_folder` in the main
  script. They no longer cause any file access.
- Line endings: the codebase uses CRLF; edited and new files are kept in CRLF.

### Reference results (2026-10-23)
- `docs/reference_results/lemon_grove_seed0/`: the outputs of the verified seed-0 run C from Phase 1, made
  **before** the restructuring. It holds the 9 reported files (`output/`) and 23 intermediate files (`intermediate/`), which help locate where
  a difference starts. `00_simulation.log` and `3-0_op-dyn_atts.csv` are left out because they change on every run.
  The README there lists the exact input parameters and how to check a code change.
- `tools/compare_reference.py`: compares the last run's files with the reference byte for byte. It ends with `REPRODUCED` or
  `NOT REPRODUCED` (exit code 0/1). FleetPy's `00_config.json` contains the codebase's absolute path, so in that one file
  the code root is replaced by a placeholder before comparing.
- **Rule from now on:** after any code change, do a full run with the reference inputs and seed, then
  `python tools/compare_reference.py` must report `REPRODUCED`.

### Verification (2026-10-23): passed
- Full run of the restructured code (seed 0) under the I/O tracer, about 30 min.
  - `tools/compare_reference.py`: **32 identical, 0 differing/missing, `REPRODUCED`**.
  - **No file access outside the codebase** except non-data items: matplotlib's font cache
    (`C:\Users\Autonomicity\.matplotlib`), the Windows null device opened while importing a library, and one directory listing of the
    tracer's own folder (it was on the import path only because the tracer lives there).
- Guard test: with `test_area=downtown_sd` and `debug_mode_list=TRUE`, the run stopped at startup with
  `ERROR: configuration ... is not self-contained (mtsm_data/) yet: test_area=['downtown_sd'] (only lemon_grove), debug_mode_list=True`
  and exit code 1. The parameter file was restored afterwards, and `check_inputs.py` passes.

### Optimizer note
- Addressed in Phase 1c, for the actual optimizer `Bayesian_optimization_script.py`.

---

## Phase 1c: optimizer reads and writes `mtsm_data/`

### Changes (2026-10-23), `Bayesian_optimization_script.py`
| What | Before | Now |
|---|---|---|
| Parameter file (read + written each call) | `Bayesian_Optimization/Input_parameter/input_parameter.csv` | `mtsm_data/input_parameter/input_parameter.csv` |
| Evaluation file (read) | `Bayesian_Optimization/lemon_grove/output_folder/lemon_grove_evaluation_zonal_partition_False.csv` | `mtsm_data/lemon_grove/output/` (same name) |
| Individual results (read) | `Bayesian_Optimization/lemon_grove/output_folder/individual_results_micro_M_…_scen_10.csv` | `mtsm_data/lemon_grove/output/` (same name) |
| Optimizer outputs (`per_call_results.csv`, `run_log.txt`, `indv_res/`, `per_itr_agg_sim_output/`, result CSVs, `indiv_call_timings_eval.csv`) | `Bayesian_Optimization/optimization_output/<folder_name>/` | `mtsm_data/lemon_grove/optimization_output/<folder_name>/` (`folder_name` is still `LG_submission_results_R2`) |
| Model launch | `run_examples_new_parking.py`, relative to the current working directory | absolute path in the codebase, `cwd` set to the codebase root, so the optimizer works from any working directory |

- New constant `mtsm_paths.LG_OPTIMIZATION_OUTPUT_DIR`. The script imports `mtsm_paths as mtsm`.
- Unchanged: the model's Python interpreter `C:/Users/Autonomicity/.conda/envs/fleetpy/python` (the environment is
  outside the codebase by nature; see Phase 2), all optimizer logic, column indices and file names.
- `New folder/MOBO_for_micro.py`: kept unchanged. It still points to the old folders.
- Earlier optimizer results in `Bayesian_Optimization/optimization_output/` were **not** moved. New optimizer runs start in
  `mtsm_data/lemon_grove/optimization_output/`.

### Verification
- The script compiles, CRLF line endings are kept, and no `D:/` path is left outside comments. **Not run.** A run takes many
  model evaluations and overwrites the parameter file.

### Consequence to keep in mind
- The optimizer overwrites `mtsm_data/input_parameter/input_parameter.csv`, which is a frozen input. After an optimizer
  session, the parameter file holds the last candidate's values. `tools/check_inputs.py` and the model's startup check will
  then report it as changed, and `tools/compare_reference.py` will not reproduce until the reference parameters are restored
  (they are listed in `docs/reference_results/README.md`). Long-term fix (Phase 3): give each run its own parameter
  file instead of editing the frozen one.
- `mtsm_data/lemon_grove/optimization_output/` is generated and git-ignored (Phase 2a).

---

## Phase 2a: git repository

### Repository (2026-10-23)
- Remote: `https://github.uci.edu/rituns/Multimodal_Transportation_System_Model`, branch `main`.
- Author for all commits: **Ritun Saha `<rituns@uci.edu>`**, set per repository (`git config user.name/user.email`).
  The machine's global git identity is a different user, so **set the identity again in every new clone**.
- Moved 2026-11-11: the repository is now `https://github.com/ritunuci/Multimodal_Transportation_System_Model`
  (clone `D:\Ritun\MTSM_project`), author **Ritun Saha `<ritunsaha95@gmail.com>`**. The old clone
  `D:\Ritun\Multimodal_Transportation_System_Model` has no remote and is kept only as an archive. The new clone was
  checked: all tracked files byte-identical to the old one, full seed-0 run **`REPRODUCED`**, `check_inputs.py` passes.
- Old clone deleted 2026-11-11 after a check: no commits, tags, stashes or untracked files were missing from the new
  clone; its git-ignored outputs were identical to the new clone's, apart from FleetPy's last-run log, config and timings.
- Two commits:
  1. **Baseline**: the codebase as found, before this reproducibility work. It still reads and writes folders outside the codebase.
  2. **Phases 1, 1b, 1c**: the current state, tagged **`v1-reproducible`**.
- The baseline's 7 changed files were reconstructed by undoing every recorded edit in reverse (a scratchpad script; each
  replacement had to match exactly once). Checks:
  - `run_examples_new_parking.py` came back to exactly 2204 lines and `Bayesian_optimization_script.py` to 640, as
    measured before any edit.
  - The changed lines sit at the same line numbers (154, 283, 2051) as read before any edit.
  - The diff between the two commits contains only the edits listed in Phases 1, 1b and 1c.
  - One unavoidable uncertainty: `folder_directory.py` is assumed to have started with one empty line (as first read),
    since the editing tool dropped it when the import was added at the top.
- No `Co-Authored-By` line in the commits (decided by the user). This document records what was changed and why.
- Line endings: `.gitattributes` contains `* -text`, so git stores and checks out **every file byte for byte**, whatever a
  machine's `core.autocrlf` is. Without it, a clone with different settings (or on Linux/macOS) could get LF versions of the
  frozen inputs and reference files, which would then fail the checksum and byte-for-byte checks. Files in the repo are CRLF.

### `.gitignore` (replaces the one inherited from FleetPy)
- Rule: **every input a run reads is tracked; everything a run writes is ignored**, so a fresh clone can reproduce
  `docs/reference_results/`.
- Ignored as run output: `studies/*/results/`, the per-iteration FleetPy demand files in
  `data/demand/lemon_grove_example_demand/matched/lemon_grove_example_network/`, the contents of
  `mtsm_data/lemon_grove/{output,final_network,indiv_output,optimization_output}/` (the folders stay via `.gitkeep`), and the networks
  rebuilt every run in `mtsm_data/lemon_grove/initial_network*/`. Exceptions keep the two frozen networks
  (`initial_super_network_non_micro_hw_20.csv` and `initial_super_network_micro_hw_20_virstop_100.csv`) tracked.
- Also ignored: `eval_output_dir/` (2023 outputs), `*.log`, the stray root `lemon_grove_debug_*_fleetpy_demand.csv`, IDE folders,
  and FleetPy's compiled C++ router (not used by this run). FleetPy's generic Python rules are kept.
- FleetPy's `data/` rules (which would have dropped the Lemon Grove network) were removed, so all of `data/`, including FleetPy's
  upstream example data, is tracked.
- Checked before committing:
  - All 23 files that the verified run reads before writing are tracked, and none of them is ignored.
  - The complete list of ignored files (570, of which 197 in the FleetPy demand folder are outputs of earlier runs) was
    reviewed: nothing else.

### Clone test (2026-10-23): passed
- Fresh clone of the two local commits into `D:\Ritun\mtsm_clone_test`: 716 tracked files, and `tools/check_inputs.py` passed.
- Full seed-0 run in the clone, under the I/O tracer: `tools/compare_reference.py` reported **32 identical, `REPRODUCED`**;
  the frozen inputs still matched afterwards; **`git status` was clean** (every generated file is ignored).
- **No access outside the clone**, and in particular none to the old `D:\Ritun\Siwei_Micro_Transit\FleetPy_SanDiego`
  folder. The only items were matplotlib's font cache, the Windows null device and the tracer's own folder. So no
  leftover absolute path into the old codebase is used.
- This result was recorded by amending commit 2 before the first push. The code tested is unchanged by the amendment.

---

## Phase 2b: environment freeze

### Plan
1. Stale-path cleanup and optimizer interpreter (below). **Done.**
2. Capture the `fleetpy` env in `env/`: `conda list --explicit --md5` (conda packages, win-64), `pip freeze` (102 of the
   135 packages come from pip, including pandas, gurobipy, networkx), `conda env export --no-builds` (readable fallback).
   `requirements.txt` is FleetPy's original and wrong for this model (numpy 1.19.5 / pandas 1.2.0 vs 2.2.6 / 2.2.3);
   replace it with a pointer to `env/`. **Done** (below).
3. Record what is outside the env: Gurobi 12.0.3 license, Windows 10. **Done** (below).
4. Optional: startup check that prints key package versions and warns if they differ from the lock. **Skipped**
   (user's decision, 2026-10-23); `python tools/export_env.py` does the full check on demand.
5. Rebuild test: new env from `env/` only, full run in a fresh clone, `REPRODUCED`. **Done, passed** (below).
6. Docs, commit, push. **Done** (`65861ec`). No `v2-env-locked` tag (user's decision).

### Step 1: stale hardcoded paths (2026-10-23)
- Scope: the modules the run imports, plus the optimizer. Standalone scripts the run never imports (`plotting_code.py`,
  `equity_analysis*.py`, `temp.py`, `result_process.py`, `pre_process/zonal_partition.py`,
  `pre_process/process_network_trial_edit.py`, `New folder/*`, `plotting_codes_old/*`, ...) still contain absolute
  paths and were **not** changed (decided by the user).
- Paths the run uses were already under the repo root since Phase 1b. What remained were about 170 live (uncommented) absolute
  paths on branches the run does not take.
- Rule applied:
  - An unused assignment on the active branch is commented out with a `# STALE:` prefix.
  - A branch or function whose folders are outside the codebase now calls `mtsm.not_self_contained(what)` (new in
    `mtsm_paths.py`), which raises `NotImplementedError` with a message pointing here. Its old lines stay as
    `# STALE:` comments. `grep -rn "STALE:"` lists them all.
- Files: `folder_directory.py`, `update_network_files.py`, `output_performance_metrics.py`, `get_microtransit_skims.py`,
  `inte_sys_mode_choice.py`, `network_algorithms.py`, `run_examples_new_parking.py` (one unused variable),
  `pre_process/process_network.py`, `pre_process/generate_demand_files.py`.
- Now stopped (with a clear error, instead of reading or writing old folders): downtown_sd, `TRPartA=False`,
  `BayesianOptimization=False` and zonal branches; the preprocessing functions that built today's frozen inputs
  (`create_mgra_pop_income_table`, `create_adjacent_MGRA_file`, `get_transit_link_route`, `construct_initial_network`,
  the demand-preparation functions in `generate_demand_files.py`); old downtown_sd functions (`MNL_choice`,
  `get_demand_nodes`, `get_microtransit_skims()`); and the files' own `__main__` test blocks.
  Note: `create_mgra_pop_income_table` would have overwritten the frozen `lemon_grove_MGRA_pop_inc.csv`; it now stops first.
- `accessibility_calculation()`: on the active branch, the fixed-route network folder (read only for
  `microtransit="non_micro"`, which the run never passes) was a stale path. It is now `None`, and that case stops.
- `create_nodes_emp_dict()`: removed a dead `super_network_emp` path built from a stale `output_folder` (never opened).
- `Bayesian_optimization_script.py`: the model is launched with `sys.executable` instead of
  `C:/Users/Autonomicity/.conda/envs/fleetpy/python`. Checked: only the `fleetpy` env has ax/torch/botorch/gurobipy
  (`fleetpy_ax` is empty), so the optimizer runs in `fleetpy` and the model gets the same interpreter as before.
- Not changed: `tools/compare_reference.py`'s `REFERENCE_CODE_ROOT` (data: where the reference run was made) and FleetPy's
  upstream `src/` example paths.

### Verification (2026-10-23): passed
- No live absolute path left in the edited files. All compile, CRLF kept, the run's modules import.
- pyflakes: every new "undefined name" comes after a `not_self_contained()` call in the same function (checked one by one).
- `determine_dolders` stops for downtown_sd, `BayesianOptimization=False` and `TRPartA=False`, and returns the `mtsm_data/`
  folders for the reference configuration.
- Full seed-0 run under the I/O tracer: `compare_reference.py` **32 identical, `REPRODUCED`**; `check_inputs.py` passes
  afterwards. Outside the codebase only matplotlib's font cache, the null device and the tracer's folder.

### Standalone scripts moved to `standalone_scripts/` (2026-10-23)
- Moved with `git mv`, unchanged (history kept): every `.py` file at the root and in `pre_process/` that the run, the
  optimizer and `tools/` do not import, plus the folders `New folder/` and `plotting_codes_old/`. 30 files in all.
  **Afterwards, the user moved the four FleetPy tools back to the root:** `run_examples.py`, `replay_pyplot.py`,
  `ScenarioCreatorGUI.py` and `scenario_creator.py` (which the GUI imports), so 26 files remain moved. The reproducibility
  check was not rerun for this (user's decision); the run imports none of them, and they are byte-identical to before.
  Subfolders keep their names (`standalone_scripts/New folder/`, `standalone_scripts/pre_process/`, ...), so earlier
  entries in this log that name `New folder/...` or `pre_process/zonal_partition.py` now mean the same files under
  `standalone_scripts/`.
  - Root (still moved): `agent_mode_path_choice_decision.py`, `equity_analysis.py`, `equity_analysis_part_2.py`,
    `headway_chek_TBD.py`, `plotting_code.py`, `result_process.py`, `temp.py`,
    `test_integrated_sys.py`, `testing_scenario_creation_backup.py`.
  - `pre_process/`: `generate_configs.py`, `process_network_trial_edit.py`, `zonal_partition.py`.
- Kept at the root: the 14 modules the run and the optimizer use (plus 3 in `pre_process/`) (static import closure, imports inside functions
  included), the empty `__init__.py`, and non-script files (`README.md`, `Input_Parameters.md`, the `.docx`/`.txt` notes).
  (2026-11-11: the `.docx`, `Micro Transit Code changing.docx`, was deleted; it held only its title, made
  2022-11-16, and nothing read it.)
- Checked before moving: no non-import references from staying code (file names in strings, `.gitignore`, `importlib`).
  `src/scenario_gui/` imports `ScenarioCreatorGUI` only under `TYPE_CHECKING`.
- Moved scripts import repo modules by name; run them from the root with `PYTHONPATH=.` (see `standalone_scripts/README.md`).
- Verification: full seed-0 run under the I/O tracer, `compare_reference.py` **32 identical, `REPRODUCED`**,
  `check_inputs.py` passes, no access to `standalone_scripts/` and nothing outside the codebase but the usual three items.
  A moved file that the run needed would have failed with `ImportError`, since it no longer exists at its old path.

### Step 2: environment lock files (2026-10-23)
- New `tools/export_env.py` (same pattern as `check_inputs.py`): `--write` creates `env/` from the running environment;
  without arguments it compares the running environment with `env/` (exit code 1 if anything differs).
  Run it with the env's own interpreter.
- `env/` (written from the `fleetpy` env, Python 3.10.19, win-64; conda 22.9.0 from `C:\ProgramData\Anaconda3`):
  - `fleetpy.conda-explicit.txt`: the 34 conda packages, URL + MD5 of each build (`conda list --explicit --md5`).
  - `fleetpy.pip.txt`: the 102 packages pip installed, `name==version`. Selected by each package's `INSTALLER`
    record (`pip`), which matches the 102 `pypi` rows of `conda list`. Not plain `pip freeze`: that writes conda's
    packages as `name @ file:///D:/bld/...` build paths, which cannot be installed elsewhere. Install with
    `pip install --no-deps` after the conda file.
  - `fleetpy.environment.yml`: `conda env export --no-builds` without the machine-specific `prefix:` line; readable,
    not exact, not used by the check.
  - `README.md`: how to recreate and check the env.
- Checked: `pip check` reports no broken requirements (so `--no-deps` gives a complete env); no pip package came from a
  local path or git URL (no `direct_url.json`); torch is PyPI's `2.9.0` (CPU build on Windows). `tzdata` is in both
  files on purpose: conda's `tzdata 2025b` (time-zone database) and pip's `tzdata 2025.2` are different packages
  (`conda list` shows one row per name, hence 135 rows for 136 packages).
- `python tools/export_env.py` right after `--write`: `environment ... matches ...` (exit code 0).
- `requirements.txt`: replaced by a comment pointing to `env/`. FleetPy's original list (numpy 1.19.5, pandas 1.2.0,
  networkx 2.3, geopandas 0.7.0, matplotlib 3.1.1, ...) is in the git history (commit `6d311ee`). FleetPy's `README.md`
  still says `conda install --file requirements.txt`; that now installs nothing.
- `.gitignore`: FleetPy's rules `env/` and `ENV/` (virtualenvs; git on Windows matches case-insensitively) ignored the new
  folder. Added `!/env/` so the repo-root `env/` is tracked.
- No model code changed, so no model run was needed. The real test of the lock files is step 5 (new env from `env/`
  only, full run in a fresh clone, `REPRODUCED`).

### Step 3: what is outside the environment (2026-10-23)
- `tools/export_env.py --write` now also writes `env/fleetpy.system.txt`: OS, CPU, Python, conda, BLAS, gurobipy, and
  the Gurobi license file's location, `TYPE`, `VERSION` and `EXPIRATION` (never the key, user name or host name).
  Regenerating left the three lock files byte-identical; the check still passes.
- `env/README.md`, new section "Outside the environment". Facts on the reference machine:
  - Windows 10 10.0.19045 (64-bit), Intel CPU (Family 6 Model 79), 12 logical CPUs; conda 22.9.0.
  - BLAS: numpy/scipy are built against Intel MKL 2024.2.2 (conda-forge `libblas ... _mkl`). MKL can choose
    CPU-dependent code paths; if a second machine does not reproduce, compare with `MKL_CBWR=COMPATIBLE`.
  - Gurobi: `ACADEMIC` license for version 12, `gurobi.lic` in the user's home folder.
    **Expired on 2026-10-21** (`GurobiError: License expired 2026-10-21` when an environment is started).
  - FleetPy's `n_cpu_per_sim` is 1, so a Gurobi solve uses one thread.
- **Why the runs of 2026-10-23 still reproduced with an expired license:** AlonsoMora repositioning
  (`AlonsoMoraRepositioning.determine_and_create_repositioning_plans`) returns before `_solve_gurobi` when no request
  was rejected since the last step. In the reference run, all 68 requests in every iteration (`indiv_output/iter_0..4`)
  have an operator and a pickup time: no rejections, so Gurobi is never started. The reference results do not depend on
  Gurobi at all.
- Consequence: any parameter set that causes rejections stops with the license error until the license is renewed.
  Renewing it is the user's action (academic license from gurobi.com, `grbgetkey`); see "Phase 2b: open issues found".

---

## Phase 2b: open issues found
- **Gurobi license expired (2026-10-21).** Renew it before any optimizer session or any scenario with rejections.
  The user will renew it.
  Renewed 2026-11-12 (expires 2027-11-12; I-01 closed, `env/fleetpy.system.txt` updated).
- ~~**Optimizer uses stale results when a model run fails.**~~ **Fixed 2026-10-23** (below). `run_script()` ignored the
  model's exit code, and `collect_output()` then read `lemon_grove_evaluation_zonal_partition_False.csv`. If a run
  stopped before writing it (e.g. the Gurobi license error), that file still held the **previous candidate's**
  results, which were recorded for the new candidate without any warning.

### Fix: optimizer stops on a failed model run (2026-10-23), `Bayesian_optimization_script.py`
- New `model_output_files(values)`: the two files `collect_output()` reads for a candidate (the evaluation file and
  `individual_results_micro_M_fsize_{d}_op_hr_15_hw_{f}_virstop_75_scen_10.csv`). `collect_output()` now uses it too.
- `run_script(values)` (was `run_script()`):
  - deletes both files **before** the model starts. The model rewrites both on every successful run (`open(..., 'w+')`),
    so this changes nothing for a good run. The individual-results file is named after fleet size and headway, so
    without this an earlier candidate with the same two values could also leave a matching stale file;
  - **after** the run raises `RuntimeError` (naming the candidate and pointing to `per_call_results.csv`) if the exit
    code is not 0, if either file is missing, or if the evaluation file has fewer than 4 rows (`collect_output()`
    reads rows 2 and 3; the model opens this file early in the run, so a crash can leave a partial one).
- Stopping (rather than skipping the candidate) keeps the optimizer honest: every candidate evaluated so far is already
  in `per_call_results.csv`, and skipping would need changes to the Bayesian-optimization loop.
- Checked that a model failure reaches the optimizer as a non-zero exit code: no `bugfix` parameter in the scenario
  configs and `run_scenarios` is called without `continue_next_after_error` (both would swallow FleetPy exceptions);
  the `except` around the convergence step re-raises; the relaunch guard passes the child's exit code on
  (`sys.exit(subprocess.call(...))`; exit code 1 shown in the Phase 1b guard test).
- Test (scratchpad, without importing the optimizer, because its import overwrites `per_call_results.csv`): the two
  functions taken from the source and run against a fake model process. Stale files were deleted before the fake model
  started; crash, crash with a partial evaluation file, exit 0 without individual results, and exit 0 with an
  incomplete evaluation file all stop with the expected message; a complete run returns normally. Compiles, CRLF kept,
  pyflakes clean. The optimizer itself was not run (Gurobi license), and the model code is unchanged, so no reference
  run was needed.
- After an optimizer session the model output folder holds the last candidate's files (as before).

### Step 5: rebuild test (2026-10-23): passed
- Fresh clone of commit `09e0684` into `D:\Ritun\mtsm_lock_test` (723 tracked files; lock files byte-exact, CRLF).
- New env built **only from the clone's `env/`**, on another drive and under another name than the original:
  `conda create -p D:\Ritun\envs\fleetpy_lock_test --file env/fleetpy.conda-explicit.txt`, then
  `python -m pip install --no-deps -r env/fleetpy.pip.txt` (`PYTHONPATH` unset, `PYTHONNOUSERSITE=1`).
- **Finding: the conda file brings no pip.** pip had upgraded itself to 25.2 in the original env, so pip counts as
  a pip package (it is in `fleetpy.pip.txt`, not in the conda file), and the new env had no pip to install the pip
  list with. Fix: `python -m ensurepip` first (installs Python's bundled pip 23.0.1; it did not touch conda's
  setuptools 80.9.0 / wheel 0.45.1), then the pip list, which replaced it with pip 25.2. `env/README.md` now has
  this step.
- Checks on the new env: `pip check`: no broken requirements; `python tools/export_env.py`:
  `environment D:\Ritun\envs\fleetpy_lock_test matches D:\Ritun\mtsm_lock_test\env` (all 34 conda and 102 pip
  packages identical). No user site-packages folder exists (`AppData\Roaming\Python\Python310`), so none leaked in.
- `tools/check_inputs.py` in the clone: all frozen inputs match.
- Full seed-0 run in the clone with the new env's Python, under the I/O tracer: `compare_reference.py` **32 identical,
  `REPRODUCED`**; `check_inputs.py` passes afterwards; the clone's `git status` is clean.
- Trace: no access to the original `fleetpy` env, to the original repo or to `Siwei_Micro_Transit`; outside the clone
  only matplotlib's font cache, the null device and the tracer's folder.
- What this proves: `env/` fully describes a working environment, and the run depends only on the repo plus that
  environment. Not proven: another machine (same CPU, Windows and MKL here); that is Phase 5.
- The test env and the test clone were deleted afterwards; the original `fleetpy` env was not touched.

---

## FleetPy as a separate module (`fleetpy/`)

### Plan (2026-11-07, decisions by the user)
- FleetPy moves into `fleetpy/`. `fleetpy_runner.py` is the only MTSM module that imports it.
- FleetPy keeps running in the same Python process. A separate process would change the results: FleetPy re-seeds
  `random`/`np.random` during a simulation (`fleetpy/src/FleetSimulationBase.py:163`,
  `fleetpy/src/fleetctrl/repositioning/RepositioningBase.py:228`), and the mode choice of the next iteration continues
  from that state.
- MTSM keeps its FleetPy-format inputs in `mtsm_data/` and copies them into `fleetpy/` before each FleetPy run.
- Steps:
  1. Compare with upstream FleetPy.
  2. Move FleetPy, add the runner and the copied inputs, remove the debug-only edits.
  3. Give the model its own vehicle type (capacity 8), with a checked reference update (I-09). Done 2026-11-08.
  4. Restore FleetPy's example data, archive the downtown San Diego data, run FleetPy's own example (I-10).
     Done 2026-11-08 as step 1 of "Removing downtown San Diego" (downtown data deleted instead of archived).
  5. Docs. Done 2026-11-08.
- Not in this pass: deleting the old, unused MTSM files inside `fleetpy/` (I-11).

### Step 1: comparison with upstream (2026-11-07)
- Upstream `https://github.com/TUM-VT/FleetPy` was downloaded read-only into the scratchpad. Base: commit `7019960`
  (2022-10-10, `main`). It contains 90 of the 97 `src/` files byte for byte (line endings ignored), more than any
  other commit. Details and all differences: `fleetpy/LOCAL_CHANGES.md`.
- Code: 4 pandas-2 fixes; 3 files with commented-out debug prints only; no change to FleetPy's logic.
  `run_examples.py` (replaced by the user, commit `13fdc29`) is FleetPy's runner with small edits.
- Data: `data/vehicles/default_vehtype.csv` has capacity 8 instead of 4 and is used by the run (I-09); FleetPy's
  example data was overwritten with downtown San Diego data (I-10); 464 files were added (I-11).

### Step 2: move, runner, copied inputs (2026-11-07)
- Moved with `git mv` (history kept) into `fleetpy/`: `src/`, `data/`, `studies/`, `run_examples.py`,
  `replay_pyplot.py`, `scenario_creator.py`, `ScenarioCreatorGUI.py`, `README.md`, `LICENSE`, `Input_Parameters.md`,
  `__init__.py`. `requirements.txt` (points to `env/`) stays at the root.
- Moved to `mtsm_data/lemon_grove/fleetpy_inputs/` (same folder layout as `fleetpy/`):
  `data/networks/lemon_grove_example_network/` (11 files),
  `data/fleetctrl/initial_vehicle_distribution/lemon_grove_example_network/imbalanced.csv` and the 28 `lemon_grove_*`
  scenario configs.
- `fleetpy_runner.py` (new):
  - puts `fleetpy/` on `sys.path` and imports `src.*`;
  - holds the functions moved unchanged from the entry script: `run_single_simulation`, `run_scenarios` (with the
    `random_seed` override), `read_outputs_for_comparison`, `warn_non_optimal_repositioning`, `check_assertions` (now
    gets the log file as an argument) and `create_config_files`;
  - new `stage_inputs(cc, sc)`: copies the two config files and `LG_STAGED_INPUTS` (network nodes, edges, `crs.info`,
    initial vehicle distribution) from `mtsm_data/lemon_grove/fleetpy_inputs/` into `fleetpy/` and returns the paths of the
    copied config files. The copies are git-ignored.
- `run_examples_new_parking.py`:
  - `import os` (it used to come from FleetPy's `from src.misc.globals import *`) and `import fleetpy_runner as fleetpy`
    instead of the `src` imports; the unused `traceback` import removed;
  - scenario configs are read from, or created in, `mtsm.LG_FLEETPY_SCENARIOS_DIR`;
  - `fleetpy.stage_inputs(cc, sc)` before each FleetPy run;
  - the old FleetPy example branch (`test_repositioning=True`, never taken) points to `fleetpy/`.
- `mtsm_paths.py`: new `FLEETPY_DIR`, `LG_FLEETPY_INPUTS_DIR`, `LG_FLEETPY_SCENARIOS_DIR`; `LG_FLEETPY_DEMAND_DIR` and
  `FLEETPY_RESULTS_DIR` are now under `fleetpy/`.
- `tools/check_inputs.py`, `mtsm_data/MANIFEST.csv`: 6 new frozen inputs (the FleetPy inputs the reference run reads), 20
  in all. The 14 existing rows are unchanged.
- `tools/compare_reference.py`: in `00_config.json`, FleetPy's root folder (the code root when the reference was made,
  now `fleetpy/`) is replaced by a placeholder.
- `.gitignore`: FleetPy's rules now start with `fleetpy/`; the copied inputs are ignored.
- Removed the commented-out debug prints (decision D7) in `src/FleetSimulationBase.py`, `src/routing/NetworkBasic.py`
  and `src/routing/routing_imports/Router.py` (all three now identical to upstream) and two lines in `run_examples.py`.
  `fleetpy/run_examples.py` keeps the LF line endings it was committed with.
- New `fleetpy/LOCAL_CHANGES.md`: base version and every local change.

### Verification (2026-11-07): passed
- pyflakes on the entry script: no new warnings (the only undefined names are the old `pre_node` and `wait_times`).
  The runner is clean. Everything compiles; CRLF kept.
- The generated outputs of earlier runs were moved to the scratchpad first, so every compared file was written by this
  run.
- Full seed-0 run under the I/O tracer: `compare_reference.py` **32 identical, `REPRODUCED`**; `check_inputs.py`
  passes; `git status` shows no generated files.
- Trace: FleetPy reads only inside `fleetpy/`, and its Lemon Grove inputs are the copies; nothing is read under the old
  root `src/`, `data/` or `studies/`, or in `standalone_scripts/`; outside the repo only matplotlib's font cache, the
  null device and the tracer's folder.

### Renames (2026-11-07)
- `mtsm/` -> `mtsm_data/` (it holds the model's data: frozen inputs and outputs, no code) and
  `test_file_backup_latest.py` -> `Bayesian_optimization_script.py`, both with `git mv`.
- Code: one line, `MTSM_DIR` in `mtsm_paths.py`; all paths are built from it. The module `mtsm_paths` (imported as
  `mtsm`) keeps its name. The optimizer needs no change (it uses `mtsm_paths` only and does not name itself).
- `.gitignore` rules, comments, messages and docs updated. `MANIFEST.csv` (paths relative to the folder) and the
  reference results (they contain no `mtsm/` path) are unchanged.
- Verification (2026-11-07): passed. Full seed-0 run under the I/O tracer: `compare_reference.py` **32 identical,
  `REPRODUCED`**; `check_inputs.py` passes; no generated files in `git status`; nothing read or written under `mtsm/`.

### Step 3: the model's own vehicle type (2026-11-08)
- New frozen input `mtsm_data/lemon_grove/fleetpy_inputs/data/vehicles/lemon_grove_vehtype.csv`: FleetPy's
  `default_vehtype.csv` as it was here (capacity 8, daily cost 2500 cent, 25 cent/km, 50 kWh, 10000 km), with only the
  name changed. `fleetpy_runner.stage_inputs` copies it into `fleetpy/data/vehicles/` (git-ignored).
- The 26 Lemon Grove scenario configs in `mtsm_data/` and `fleetpy_runner.create_config_files` use
  `lemon_grove_vehtype:N` instead of `default_vehtype:N`.
- `fleetpy/data/vehicles/default_vehtype.csv` and `low_range_vehtype.csv` restored from upstream `7019960`, byte
  for byte (capacity 4).
- `tools/check_inputs.py` and `mtsm_data/MANIFEST.csv`: the vehicle file added (21 frozen inputs); the checksum of
  `lemon_grove_example_ir_heuristics_repositioning_2_veh.csv` updated (only the type name changed). Before
  `--write`, `check_inputs.py` reported exactly that one config as changed.
- Verification (2026-11-08): full seed-0 run under the I/O tracer. `compare_reference.py`: 28 identical, 4 differing,
  exactly the 4 FleetPy files that contain the vehicle-type name (`00_config.json`, `2-0_op-stats.csv`,
  `2_vehicle_types.csv`, `standard_mod-0_veh_eval.csv`; 280 occurrences). Each was byte-identical to the run after
  replacing the old name with the new one, so the reference was updated by that replacement (documented in
  `docs/reference_results/README.md`). Then **32 identical, `REPRODUCED`**; `check_inputs.py` passes; no generated
  files in `git status`. The 9 reported results never differed. The trace shows FleetPy reading the copied
  `lemon_grove_vehtype.csv`.

### Step 5: docs and result (2026-11-08)
- `fleetpy/LOCAL_CHANGES.md` final: a summary of how this FleetPy differs from upstream `7019960`, the current state
  of its data first, then the history of the undone data changes; line endings described as they are.
- "Continuing work in a fresh clone": rules for `fleetpy/` added.
- Result: FleetPy is upstream `7019960` with four pandas-2 fixes, small `run_examples.py` edits and one README line;
  it holds no MTSM parameter or input. MTSM reaches it only through `fleetpy_runner.py`, in the same process, and
  copies its own inputs (network, initial vehicle distribution, vehicle type, scenario configs) from
  `mtsm_data/lemon_grove/fleetpy_inputs/` into `fleetpy/` before each run. Still open: old unused MTSM files inside
  `fleetpy/` (I-11) and FleetPy's own example a) serving 90 instead of 88 users (I-12).
- Docs only, no run needed.

---

## Removing downtown San Diego

### Plan (2026-11-08, decisions by the user)
- Goal: remove all downtown San Diego code (also commented code) and its input and output files; the model is
  Lemon Grove only. The Lemon Grove reference run must still reproduce after each step.
- Steps: 0) mark the last commit with downtown; 1) FleetPy data; 2) code in the run; 3) docs.
- Decisions: tag the last commit with downtown (D1); `standalone_scripts/` is not touched, since nothing runs it
  (D2); other dead branches (`TRPartA=False`, `BayesianOptimization=False`, debug mode) are left for later (D3); git
  history is kept, so the files can be recovered (D4). Step 1 replaces step 4 of the FleetPy separation (D6 there):
  the downtown files are deleted instead of archived.

### Step 0: marker (2026-11-08)
- Annotated tag `last-with-downtown-sd` on `4329154`, the last commit with downtown San Diego code and data. It is
  local until pushed (`git push origin last-with-downtown-sd`).

### Step 1: FleetPy data (2026-11-08)
- Every file in `fleetpy/data/` and `fleetpy/studies/` was compared with upstream `7019960`. The downtown files had
  FleetPy's example names (`example_network`, `example_demand`), so they were identified by node IDs: the downtown
  network has nodes 0-731, FRT stops 732-871 and microtransit nodes from 872 (FleetPy's Munich network: 7,617 nodes;
  Lemon Grove: 0-2269).
- Restored from upstream, byte for byte: the 14 overwritten example files (I-10, closed).
- Deleted (`git rm`): 283 downtown demand files and plots, 7 downtown network files, 33 downtown scenario configs
  (`downtown_sd_*`, and `example_pool_1000_rq_*`, whose demand `example_1000.csv` has only downtown node IDs), and
  10 files that only existed because the originals had been overwritten (FleetPy's moved-aside Munich demand and
  two backups).
- Kept: 13 old scenario configs whose study area could not be determined (I-11), the Lemon Grove leftovers (I-11)
  and FleetPy's vehicle files (vehicle-type step, I-09).
- After this step, `fleetpy/` differs from upstream only by the code changes in `fleetpy/LOCAL_CHANGES.md`, the
  vehicle files and the files listed under I-11.
- FleetPy's own example a) runs on the restored data, but serves 90 users where its check expects 88, also with
  upstream's vehicle capacity (I-12).
- Verification (2026-11-08): passed. Full seed-0 run under the I/O tracer: `compare_reference.py` **32 identical,
  `REPRODUCED`**; `check_inputs.py` passes; no generated files in `git status`; FleetPy read no example or
  downtown file (only the copied Lemon Grove inputs and the vehicle types).

### Step 2: code in the run (2026-11-08)
- Removed from the files the run executes: every `study_area == "downtown_sd"` branch, the downtown-only constants
  (node ranges 731/732-871/872-1603, accessibility thresholds 34986/43787, fallback employment values, per-route
  speeds), the flag `dt_sd_full_trnst_ntwk` (from 11 function definitions and their calls), and the `# STALE:` and
  other comments that held downtown paths (`Data/0719_input/` outside `lemon_grove/`, `Downtown_SD_*`,
  `Bayesian_Optimization/downtown_sd`). Files: `run_examples_new_parking.py`, `folder_directory.py`,
  `network_algorithms.py`, `output_performance_metrics.py` (also its `__main__` test now names `lemon_grove`),
  `update_network_files.py`, `get_microtransit_skims.py`, `Bayesian_optimization_script.py` (comments only), and
  the independent downtown blocks in `pre_process/generate_demand_files.py` and `pre_process/process_network.py`.
- Where Lemon Grove was the `else:` of a downtown `if` (microtransit node mapping in the entry script), the Lemon
  Grove code now runs unconditionally; the run only allows `lemon_grove`.
- Left, for a decision: (a) the old mode-choice functions marked "old downtown_sd version" in
  `inte_sys_mode_choice.py` (`get_demand_nodes`, `MNL_choice` and the functions that use them) and
  `get_microtransit_skims.get_microtransit_skims`; nothing calls them. (b) Preprocessing in `pre_process/` that
  builds both areas: `process_network.get_transit_link_route`, `construct_initial_network` and the `__main__`
  network construction (`new_downtown_sd=True`), and `generate_demand_files.py`'s `__main__`. (c) The `micro_only`
  branch of `update_network_files.update_network_files` uses the downtown limit `from_node <= 731` without a study
  area check; the run never takes it (`microtransit_running_scenarios = ["micro"]`).
- Checks: compiles; pyflakes reports no new warnings (4 old undefined names went away with a deleted block); CRLF
  kept.
- Verification (2026-11-08): passed. Full seed-0 run under the I/O tracer: `compare_reference.py` **32 identical,
  `REPRODUCED`**; `check_inputs.py` passes; no generated files in `git status`.

### Step 2b: decisions on what step 2 left (2026-11-08, decisions by the user)
- Old mode-choice code deleted: `inte_sys_mode_choice.py` (a 3-mode multinomial / nested logit for downtown San
  Diego, superseded by the binary logit in `binary_choice.py`), and `get_microtransit_skims()` and
  `get_dmd_node_vir_stop()` in `get_microtransit_skims.py`. Nothing called them. Removed the imports that were then
  unused (`mt`, `inte_sys_mode_choice`, `auto`, `wt` in the entry script; `auto`, `mt`, `wt` in `binary_choice.py`;
  `math` in `get_microtransit_skims.py`). `get_auto_skims.py` and `get_walk_transit_skims.py` are kept but no run
  code imports them now.
- `pre_process/process_network.py` split: `update_initial_net_with_bayesian_headway`, the only function a run uses
  (sets the FRT headway in the initial super-networks), moved unchanged (byte-identical) to the new root module
  `update_initial_network.py`; the entry script imports it from there. `process_network.py` keeps the one-time
  network preprocessing (and loses its now unused `shutil` import).
- The `micro_only` branch with the downtown node limit is left as it is: I-13.
- The downtown parts of the preprocessing (`process_network.py`, `generate_demand_files.py` `__main__`) are kept
  unchanged, as the record of how the frozen inputs were made (user's decision): I-14.

### Step 3: docs (2026-11-08)
- `README.md`: the study-area note says downtown San Diego was removed (tag `last-with-downtown-sd`) and points to
  I-14; the layout table lists `update_initial_network.py` (updated in step 2b).
- `docs/open_issues.md`: I-05 names the new location of `update_initial_net_with_bayesian_headway()`; I-10 closed
  (step 1); I-13 and I-14 added (step 2b).
- `fleetpy/LOCAL_CHANGES.md`: updated in step 1.
- `standalone_scripts/` and `READ_ME_THIS_IS_IMPORTANT.txt` (the record of the TR Part A submission) are not
  changed. Docs only, no run needed.
- Removing downtown San Diego is done.
- Checks: compiles; pyflakes reports no new warnings; CRLF kept.
- Verification (2026-11-08): passed. Full seed-0 run under the I/O tracer: `compare_reference.py` **32 identical,
  `REPRODUCED`**; `check_inputs.py` passes; no generated files in `git status`.

---

## Removing the TRPartA, BayesianOptimization and debug_mode branches (2026-11-09)

- Decision by the user: simplify the code to the one configuration it runs (`TRPartA=TRUE`,
  `BayesianOptimization=TRUE`, `debug_mode_list=FALSE`), but keep the three columns in `input_parameter.csv`, because
  the optimizer writes its parameters by column position. Removing the columns and changing the optimizer is a later
  step (I-15).
- What the flags did: `BayesianOptimization` only chose folders (`FALSE` = old `TR_PartA/Data` folders, already
  refused). `TRPartA` also chose folders, and its `FALSE` branches were an older evaluation mode: other evaluation
  file name, other individual-results columns, FRT-only base case computed per scenario combination instead of
  once in the first test scenario. `debug_mode` chose `debug_*` input and config files and smaller scenario lists.
  All three were always TRUE / TRUE / FALSE (input file, startup check; the optimizer never changes them).
- Code: every `if TRPartA == True` / `if BayesianOptimization == True` block replaced by its `TRUE` branch, every
  `if debug_mode == True` block by its `else` branch (`run_examples_new_parking.py`, `output_performance_metrics.py`,
  `update_network_files.py`, `folder_directory.py`); the four combined conditions
  `(... and TRPartA==False) or (TRPartA==True and test_scenario==TRPartA_test_scenario_list[0])` became
  `test_scenario == TRPartA_test_scenario_list[0]`; the loop `for debug_mode in debug_mode_list:` removed (its body
  un-indented by 4 spaces); the flags removed from 9 function signatures and their calls, including
  `fleetpy_runner.create_config_files`. File names keep the text `debug_False` (it was `debug_%s` with
  `debug_mode=False`), so every output name is unchanged.
- Kept: reading the three columns and the startup check, which still refuses other values (message now "not
  supported"). The `__main__` test harnesses of `output_performance_metrics.py` and `update_network_files.py` keep
  their own local `debug_mode` variable (debug tools, not the run's flag).
- Checks: compiles; pyflakes reports no new warnings; CRLF kept; reviewed with `git diff -w`.
- Verification (2026-11-09): passed. Full seed-0 run under the I/O tracer: `compare_reference.py` **32 identical,
  `REPRODUCED`**; `check_inputs.py` passes; no generated files in `git status`.

## Restructuring the entry script (2026-11-09)

- Plan, decisions and the details of each step: `docs/entry_script_refactor_plan.md`.
- Result: `run_examples_new_parking.py` went from 1,921 lines (one `__main__` block, nested up to 18 levels) to 43
  lines; the model is in the package `mtsm_model/` (code map: `README.md`). The entry script keeps its name, so the
  optimizer is unchanged.
- Decisions by the user: remove `test_repositioning`, `iteration_debug`, `zonal_partition` and the commented-out
  code; keep the aggregate convergence test (commented, unfinished: I-16), `micro_only` and `non_micro`, the
  ability to run several scenarios, and the commented-out "Ritun added" demand-upscaling block with its `syn_rq`
  import (now in `mtsm_model/microtransit.py`).
- Method: 9 small steps, each only moving code into functions. Before each move, the variables the code reads and
  sets were listed with Python's `ast` module, to find values carried over from an earlier traveler, iteration or
  scenario; the order of the random draws, of dict insertions and of floating-point sums was kept.
- Found and recorded, not changed: I-16 (aggregate convergence test unfinished), I-17 (travelers who keep their
  transit choice resubmit only their last leg), I-18 (in later fare scenarios, the parking values of one traveler
  are used for all); the location of the duplicate base-case row (I-04).
- Commits: `1e38609` (plan), `e94e2f4`, `65e975c`, `f7a13f3`, `8d92eb0`, `e95d484`, `4045d72`, `171d243`, `6cbc0eb`
  (steps 1-8), step 9 (docs).
- Verification: after each of steps 1-8 a full seed-0 run under the I/O tracer: `compare_reference.py` **32
  identical, `REPRODUCED`**; `check_inputs.py` passes; no new pyflakes warnings. Step 9 is docs only.

## Only fare scenario 10 (2026-11-09)

- Decision by the user: the model uses only fare scenario 10 from now on. Drop scenarios 0-9, the fare-scenario loop
  and the path cache; keep the column `TRPartA_test_scenario_list` in `input_parameter.csv` (the optimizer writes the
  file by column position), with an open item to drop it later (I-15).
- What the other scenarios did (for the record; the last version with them is commit `3c11671`): 0 base fares;
  1 low-income discount; 2 time-based and 3 accessibility-based fare (both behaved like 0, because a later block
  reset their factor to 1); 4 transfer discounts; 5 microtransit flat fare; 6 start + distance fare; 7 = 4 + 6;
  8 time-based without peak surcharge; 9 accessibility-based without surcharge.
- Code: `network_algorithms.generalized_cost_dijsktra_OD_heap` has no `test_scenario` parameter any more and applies
  scenario 10's rules (peak factor `PkFareFactor` / `OffPkFareFactor`; `Micro2FixedFactor` on the FRT fare after
  microtransit; `Fixed2MicroFactor` on the distance fare after FRT and on the start fare; rejection penalty).
  The car path used to pass scenario 0: the car network has only link type 7, which no fare rule touches. The
  FRT-only base case has no microtransit links. `low_income_factor` and `acc_factor` (always 1 in scenario 10) were
  removed from the distance fare: multiplying by 1 is exact. The fare-scenario loop in `mtsm_model/scenarios.py`,
  `paths.PathCache` and the "first fare scenario" conditions in `results.py` were removed (the base-case rows are
  written as before; I-18 closed). The number 10 stays as `config.FARE_SCENARIO` in the output file names
  (`..._scen_10`, read by the optimizer) and the evaluation rows. The startup check refuses any other value in the
  column.
- Found: the start fare always gets `Fixed2MicroFactor` (I-19, not changed).
- Verification (2026-11-09): passed. Full seed-0 run under the I/O tracer: `compare_reference.py` **32 identical,
  `REPRODUCED`**; `check_inputs.py` passes; no new pyflakes warnings; `network_algorithms.py` reviewed with
  `git diff -w`.

## Unused code removed from `network_algorithms.py` (2026-11-09)

- Which parts a run uses was found from the import graph of the entry script and the attributes each importer
  uses: `read_request` (+ `Agent`), `read_super_network` (+ `Link`), `getTrajectory_O_to_D`,
  `generalized_cost_dijsktra_OD_heap` (+ `get_link_type_from_O_to_D`).
- Removed: class `Node`, `distance()` and `generalized_dijsktra_source_to_all()` (used nowhere, also not by the
  standalone scripts); the `__main__` test harness (it stopped at once and used an old signature); 22 of 27 import
  statements (duplicates and unused: pandas, numpy, scipy, matplotlib, setuptools, Cython, ...; the environment is
  unchanged); in the functions the run uses: the `verbose` print blocks (every caller passes `verbose=False`; the
  parameter stays), no-op `aaa = ...` lines, two unused locals (`rq_id`, `num_transit_links`) and two in
  `read_super_network`, and commented-out code. 858 -> 596 lines.
- Not changed (user's decision): the five functions only the skim modules use, and class `Link` (I-20).
- Checks: the five skim functions and `Link` are byte-identical to before; `Agent`, `read_request` and the two
  trajectory functions are identical in code (comments only removed); in `read_super_network` and
  `generalized_cost_dijsktra_OD_heap` the only code differences are the removed lines listed above;
  `get_auto_skims` and `get_walk_transit_skims` still import; CRLF kept.
- Verification (2026-11-09): passed. Full seed-0 run under the I/O tracer: `compare_reference.py` **32 identical,
  `REPRODUCED`**; `check_inputs.py` passes.

## Faster least-cost path search (2026-11-10)

- Why: a timed run showed that `network_algorithms.generalized_cost_dijsktra_OD_heap` takes 86% of the run time
  (926 of 1,077 s; 67,356 calls). Plan, measurements and the user's decisions: `docs/path_search_speedup_plan.md`.
- Code (only this function; same signature and return values): the two path flags for the transfer discounts
  (`IsMicroLink`, `IsFixedLink`) are carried along the path instead of walking back to the origin for every node
  (`get_link_type_from_O_to_D` removed); outdated heap entries of settled nodes are skipped; each network's links
  are read once into lists (`out_links`, kept on the graph); the unused set of all nodes is no longer built;
  `Heap_Node` is at module level with `__slots__`, its comparison unchanged (ties come out as before). New guard:
  a negative generalized link cost stops the run with a `ValueError` (the search relies on costs >= 0).
- Console only: the debug line `WAITING LINK = 180` can appear fewer times (outdated entries are not processed
  again); the reference run prints it 0 times.
- Verification (2026-11-10): passed. Equivalence test against the old function: 3,742 travelers × 14 cases, 52,388
  calls, 0 differing (dicts also in key order). Full seed-0 run under the I/O tracer: **6 min 58 s** (before
  17 min 53 s); `compare_reference.py` **32 identical, `REPRODUCED`**; `check_inputs.py` passes.

## Car and FRT paths reused across iterations (2026-11-10)

- Why: the car and FRT paths of a traveler are the same in every iteration. Their networks do not change (the car
  network is read once; the FRT-only network `initial_super_network_non_micro_hw_20.csv` is re-read but never
  written during a run, checked with the I/O trace), nor do the traveler and the fares. Of the arguments that change
  between iterations, `total_rejection_penalty` acts only on microtransit waiting links (type 5), which the FRT
  network does not have, and `iteration` only on the debug print on those links. The search draws no random numbers.
  Searching them once removes about 55% of the searches.
- Decisions by the user (all as recommended): (1) keep only the values read later (the full results would take
  about 1.9 GB: 0.24 MB per traveler for the car path, 0.26 MB for the FRT path); (2) the microtransit path is
  still searched every iteration, also outside the operating periods, where it runs on the FRT network (it would
  save about 5–7 s, for a second condition); (3) the store lasts one scenario, so nothing is carried from one
  scenario to the next (the kind of carry-over of I-18); (4) a guard on the FRT network.
- Code: `mtsm_model/model.py` `run_scenario` creates `fixed_paths = {}` (rq_id -> parking_dur, bt_c_gas, car path,
  FRT path) before the iteration loop and passes it to `run_iteration`. `mtsm_model/iteration.py` searches the two
  paths only for a traveler not yet in the store, then reads them from it. `mtsm_model/paths.py`: `dest_only` keeps
  the four destination values (as one-entry dicts, so the callers are unchanged) and the trajectories and drops
  `path` / `time_path`; `check_frt_network_reusable` stops the run with a `ValueError` if the FRT-only network has a
  link of type 5 (checked when the store is empty).
- Verification (2026-11-10): passed. Full seed-0 run (with stage timers): **5 min 08 s** (before 6 min 58 s); car and
  FRT searches 3,742 each (before 22,452); `compare_reference.py` **32 identical, `REPRODUCED`**;
  `check_inputs.py` passes; no pyflakes warnings in the three files.

## Helper modules moved to `mtsm_model/helpers/` (2026-11-10)

- Moved with `git mv` (history kept): the 10 helper modules a run uses, `network_algorithms`, `binary_choice`,
  `convergence_test`, `folder_directory`, `fleetpy_runner`, `output_performance_metrics`,
  `testing_scenario_creation`, `update_initial_network`, `update_network_files`, `get_microtransit_skims`; new
  `mtsm_model/helpers/__init__.py`.
- Kept at the root (user's decisions, as recommended): the entry script and `Bayesian_optimization_script.py`;
  `mtsm_paths.py`, because it derives every folder from its own location (`CODE_ROOT`) and is also used by
  `tools/`, `pre_process/` and the optimizer; `get_auto_skims.py` and `get_walk_transit_skims.py`, left for the I-20
  decision.
- Imports: every whole-line `import X as Y` of these modules became `from mtsm_model.helpers import X as Y` (aliases
  kept, so no other code changed): 52 lines, in `mtsm_model/` (13), the moved modules (4), the two skim scripts (2)
  and, by the user's decision, `standalone_scripts/` (33: the four `New folder/run_examples_new*.py` and
  `test_integrated_sys.py`; only import lines). Commented-out imports were left as they were. None of the moved
  modules depends on its own location (`__file__` is used only in `mtsm_paths.py` and `tools/`).
- Docs: README layout table and code map (new helper table), `mtsm_model/__init__.py`, `standalone_scripts/README.md`,
  I-20. Historical entries in this file keep the old paths.
- Verification (2026-11-10): passed. All model and helper modules and the two skim scripts import; the edited
  standalone scripts compile; no import of the old root names is left. Full seed-0 run under the I/O tracer:
  4 min 43 s; `compare_reference.py` **32 identical, `REPRODUCED`**; `check_inputs.py` passes.

## One parameter file (2026-11-10)

Plan, decisions and the details of each step: `docs/constant_config_plan.md`.

- `mtsm_data/input_parameter/mtsm_constant_configurations.csv`: all 53 MTSM parameters, one row each
  (`parameter_name,parameter_value,description`; no code reads the description). Keys and types:
  `mtsm_model/mtsm_global_parameters.py` (`G_<NAME> = "<name>"`, `PARAMETER_TYPES`). A frozen input.
- `config.read_constant_config()` reads it once at import into `config.PARAMETERS` and stops on a wrong header, an
  unknown, repeated or missing key, or a value of the wrong type. The constants of `config.py` keep their names and
  take their values from it; the values that were written into the code (costs, node ranges, operating hours, FRT
  line duration, default waiting time, accessibility thresholds, ...) are read as `config.PARAMETERS[gp.G_<NAME>]`
  or from derived constants in `config.py` (`LAST_WALK_NODE`, ..., `microtransit_operating_hours()`).
- Left where they were (user's decision): the FleetPy check "expected 88 users", the betas and parking durations in
  the demand file, FleetPy's constant config and scenario files, the vehicle type. Also left: the literals in the
  `__main__` blocks and in functions the run does not call, the `/ 2` rules, the `"lemon_grove"` name checks.
- `run_examples_new_parking.py --config <file>` runs with another parameter file (passed to `config.py` in
  `MTSM_CONFIG_FILE`); the startup prints which values differ from the frozen file. The optimizer writes each
  candidate's copy by parameter name into `<folder_name>/candidate_configs/` and never changes the frozen file.
  `input_parameter.csv` was deleted; I-02 and I-15 closed.
- Kept apart, to keep the results identical: meters per mile 1609.34, 1609 and 1.609 km (three keys; merging them
  changes results and needs a new reference; open item `docs/open_issues.md`, I-21).
- Verification: after each of the four code steps a full seed-0 run printed `REPRODUCED` (32 files, about 4:45);
  `tools/check_constant_config.py` compared every value and type with the old ones (`SAME: 53 parameters`; deleted
  with this step); the old and the new optimizer writer gave the same values and types on three candidates.

## Skim scripts deleted (2026-11-11)

- Deleted (user's decision, I-20 option 3; git keeps the history): `get_auto_skims.py` and
  `get_walk_transit_skims.py` (all-to-all shortest paths), and the five functions of
  `mtsm_model/helpers/network_algorithms.py` only they used: `read_network`, `read_walking_network`,
  `read_network_dist`, `dijsktra_source_to_all`, `dijsktra_all_to_all`; also the imports `OrderedDict` and
  `collections`, used only by these. Class `Link` stays (`read_super_network` uses it). 186 lines removed.
- Before: no code imported the two modules except the four `standalone_scripts/New folder/run_examples_new*.py`,
  which never call them; no skim file is an input. Those four scripts now fail at the import (they were already
  broken by the old `determine_folders` signature; `standalone_scripts/` left untouched).
- Docs: README layout table, I-20 closed.
- Verification (2026-11-11): passed. Full seed-0 run under the I/O tracer: `compare_reference.py` **32 identical,
  `REPRODUCED`**; `check_inputs.py` passes.

## FRT <-> microtransit transfers checked (2026-11-11)

- Checked with a read-only script on the reference run's final networks (AM-PM, 3,472 travelers): the model's path
  search, rewritten with the same link costs (same costs as the model's function), against an exact search with one
  label per (node, microtransit used, FRT used, previous link FRT waiting).
- Any number of transfers is possible (they go through a walk node). Reference paths: walk 1597, FRT 1075,
  microtransit 629, microtransit -> FRT 117, FRT -> microtransit 39, microtransit -> FRT -> microtransit 15. No
  transfer penalty; the networks have no transfer links (type 3), so `bt_f_trfer` has no effect.
- Found: the search can miss the least-cost path when a transfer discount applies (I-22, open; 405 travelers with
  the reference factors); the discounted FRT fare after microtransit was also charged on alighting (I-23).
- Fixed I-23 (`network_algorithms.py`): the discount is set only on boarding (walk node -> stop). With both factors
  0.5, microtransit -> FRT paths now pay 0.5 x the FRT fare instead of 1.0 x.
- Fare rules to decide (I-24): the discount holds for the whole trip after the other mode, and a re-boarding
  after an alighting is free without microtransit but charged the discounted fare after it.
- Verification (2026-11-11): passed. Full seed-0 run under the I/O tracer: `compare_reference.py` **32 identical,
  `REPRODUCED`**; `check_inputs.py` passes (the reference has `micro2fixed_factor` 0, so the fix changes nothing in it).

## Transfer penalty behind a switch; link type 3 removed (2026-11-11)

- User's decisions (all as recommended): a transfer is every transit boarding after the first (FRT <-> microtransit,
  FRT -> FRT, microtransit -> microtransit) and a route change at a shared stop; each costs `bt_f_trfer` in the
  generalized cost; behind the new parameter `enable_num_transfer_penalty` (`False`: results unchanged; I-25 is the
  reminder to turn it on with a new reference).
- `mtsm_constant_configurations.csv`: new row `enable_num_transfer_penalty,False` (key
  `G_ENABLE_NUM_TRANSFER_PENALTY`, BOOL); `MANIFEST.csv` regenerated (only this file's size and checksum changed).
- `network_algorithms.generalized_cost_dijsktra_OD_heap`: reads the switch once; when on, adds `bt_f_trfer` at an FRT
  or microtransit boarding of a path that used FRT or microtransit before, and at an FRT link after an FRT link of
  another route. The mode choice takes the search's cost, so the penalty reaches it without other changes.
- Link type 3 (FRT transfer link) removed: no network had one, so its branch never ran and `bt_f_trfer` had no
  effect. Removed the branch in the search and the `== 3` checks and the type 3 text in `trip_legs.py`;
  `network_algorithms.KNOWN_LINK_TYPES = {0, 1, 2, 4, 5, 7}`, and `read_super_network` stops on any other type
  (without the guard, an unknown link type would get the previous link's cost).
- Checks: with the switch on (a `--config` copy) and off, on the final networks, every path's cost equals its link
  costs plus `bt_f_trfer` x the transfers counted on it (6,944 paths each); transfer counts in I-25. Full seed-0 run
  with the switch off under the I/O tracer: `compare_reference.py` **32 identical, `REPRODUCED`**; `check_inputs.py`
  passes. A full run with the switch on stopped after 11 s in FleetPy, not because of the penalty: any run with
  `--config` did (`scenarios.py` handed the command line to FleetPy; fixed in the next section, I-26).

## Runs with `--config` fixed (2026-11-11)

- `scenarios.scenarios()` called `fleetpy.run_scenarios(*sys.argv)` when the program had any command-line argument
  (a leftover of FleetPy's example script), so every run with `--config` stopped at once, and with it every
  optimizer candidate since config step 4 (2026-11-10). Branch removed; the scenario always runs (I-26).
- Verification (2026-11-11): passed. Full seed-0 runs: without `--config` under the I/O tracer **`REPRODUCED`**
  (`check_inputs.py` passes); with `--config` and a copy of the frozen file **`REPRODUCED`** (the optimizer's way
  of starting the model); with `--config` and `enable_num_transfer_penalty=True`: runs to the end, results differ
  (numbers in I-25).

## Super-network script (2026-11-11)

- `pre_process/build_super_network.py` builds a super-network from a road network (walk and microtransit: nodes
  with coordinates, edges with distance and car travel time) and an FRT network (stops with coordinates, edges with
  distance, travel time and route); variants `micro` and `non_micro`, the FRT headway, the virtual stops (a list,
  or a share with a seed). No model code uses it yet (user's request); it is not a frozen input. Usage and the
  layers, link types and link order: the module docstring.
- How the frozen Lemon Grove super-networks are built (found from the data): walk nodes 0-1098 = FleetPy's nodes;
  FRT stops after them; microtransit node = walk node + offset. Walk links: every road edge, time = distance /
  1.251 m/s (the old `process_network.py` says 1.6). Microtransit links: every road edge, time = car time x 1.4
  (all 2,816; four "exceptions" reported earlier came from a comparison that matched parallel links by node
  pair). FRT waiting: boarding half the headway, alighting 0 s. Microtransit waiting: 180 s at the virtual
  stops (75 %: 815 nodes), alighting 0 s. No transfer links. CRLF, values written as Python floats.
- User's decisions: (1) each stop is joined to the nearest walk node by coordinates (both files have coordinates for
  all nodes); (2) only stops with FRT links are numbered (for Lemon Grove the offset would be 1170, not 1171: stop
  1159 has no link); (3) walk speed 1.251 m/s and factor 1.4 as defaults; (4) see above; (5) compare the content.
  Also: a tie in the nearest node goes to the smaller node number; with a share, the virtual stops are drawn with
  `random.Random(seed)` (the old code drew them without a seed).
- Check (2026-11-11, a scratch script): inputs made from the frozen data (FleetPy's nodes.csv / edges.csv; FRT edges
  = the type 1 links of the super-network, which have more digits than `super_network_transit_edges.csv`; each stop
  at its walk node's coordinates, stop 1159 added without links; the virtual stops from the type 5 links). The four
  frozen super-networks (micro hw 10 / 75 %, non_micro hw 10, non_micro hw 20, micro hw 20 / 100 %) were rebuilt
  **byte for byte**, with every node number above 1159 lowered by one. Stops moved off their node by 40 % of the
  distance to the next node (8-194 ft) gave the same network; a share with the same seed gives the same file, another
  seed another one. The frozen data has no stop coordinates (the old code read them from an outside folder), so the
  nearest-node step was checked only this way.
- Added the same day (user's request): the variant `micro_only` (microtransit without FRT: types 0, 4, 5; nodes
  numbered like `micro`, the stops without links, because the model has one `microtransit_node_offset`) and the
  car network (`--auto-out`: every road edge, type 7, route -1; the model reads it as `auto_edges.csv`). Checked:
  the car network equals `initial_network/auto_edges.csv` byte for byte; `micro_only` equals the frozen micro
  network (hw 10, 75 %) without its type 1 and 2 links, after the same renumbering (there is no frozen
  `micro_only` network). The four checks above still pass.

## Optimizer: first session since the changes, MKL crash fixed (2026-11-12)

- Test session (user's request): `Bayesian_optimization_script.py` with 5 Sobol samples and 2 optimization iterations,
  through a scratch launcher that replaces `N_BATCH`, `n_samples` and `folder_name` in memory (the script's own values,
  390 / 170 / `LG_submission_results_R2`, are unchanged).
- First try: the 5 Sobol candidates ran (parameter files written, model started with `--config`, results collected);
  then the process ended with exit code 127 at the first Gaussian-process fit. Cause: numpy/scipy LAPACK calls crash in
  the `fleetpy` env with MKL's default threading (I-27). The model never calls LAPACK.
- Fix (user's decision): the optimizer sets `MKL_THREADING_LAYER=SEQUENTIAL` before importing numpy; a value already
  set in the environment is kept. The environment in `env/` is unchanged.
- Verification (2026-11-12): with the variable, the session ran to the end in 58 min: 7 model runs (fleet 2-6,
  headway 12-30, one with headway 20), all converged, no rejected requests; `per_call_results.csv`, the candidate
  parameter files, the hypervolumes and the non-dominated set written; `check_inputs.py` passes. Full seed-0 run with
  the variable set: `compare_reference.py` **32 identical, `REPRODUCED`**. After the change to the script, its
  Ax/BoTorch part ran to the end without the variable set outside (model runs replaced by fixed values). The test
  folder was deleted (results not needed). I-03 stays open for the checks not made (see there).
- Also 2026-11-12: Gurobi license renewed (I-01 closed). `aggregation=census_track` tested with a `--config` copy:
  the run converged (7:17 min); results differ from the reference, as expected (not recorded as a reference).

## Base case's subsidy at the base FRT headway; reference updated (2026-11-12)

- Found through the user's question on the optimizer test results: a larger subsidy objective did not come with a
  larger logsum increase. Cause (I-28): the base case's subsidy used the FRT operating cost of the scenario's headway,
  so that cost cancelled in the subsidy objective, while the logsum increase is measured against the base headway.
- User's decision: the base case uses `base_frt_headway` and `base_frt_fare`, whatever the candidate's values. This
  fix gets its own new reference; the other result-changing changes (I-19, I-21, I-22, I-24, I-25) still wait.
- Change (`mtsm_model/results.py` only): base subsidy from `F_oper_cost_base`; base rows show the base headway and its
  FRT vehicle miles. The fare was already the base fare.
- Comparison with the old reference: 31 of 32 files identical; the evaluation file differs only in 13 columns of the
  two base rows, with the predicted values (base `tot_sub` 4688.83 -> 2320.67); the microtransit row is identical.
  A run with `frt_headway` 30 (`--config` copy) gave the same base row, except two accessibility columns (left, I-28).
- Reference re-established: the evaluation file in `docs/reference_results/lemon_grove_seed0/output/` was replaced by
  the new one (`docs/reference_results/README.md`, "Changes to this reference"); a second, independent full run then
  gave `compare_reference.py` **32 identical, `REPRODUCED`**; `check_inputs.py` passes.
- Optimizer: its subsidy objective changes with the evaluation file (reference run: -3092.8 -> -5461.0); earlier
  sessions are not comparable (conversion in I-28). `ref_point` widened from -15000 to -18000 (user's decision).

## Later option: compile the path search with Numba (held, 2026-11-10)

The user may consider this later; nothing has been done. After rows 2i and 2j the microtransit path searches take
about half of the 5-minute run (152 of 310 s); FleetPy, the mode choice and writing the results would not get faster.

- Idea: compile `network_algorithms.generalized_cost_dijsktra_OD_heap` with Numba (machine code at the first call;
  no C compiler needed). Cython was ruled out: it needs a C compiler (Microsoft Visual C++ Build Tools, not on this
  machine) and a build step on every machine. Numba is not installed in the `fleetpy` env (it would also bring
  `llvmlite`; `env/` and the env rebuild test would need updating).
- Needed for byte-identical results: the networks as flat arrays (the compiled form of `out_links`); a copy of
  Python's `heapq` algorithm comparing on cost only, as `Heap_Node` does (Numba's own `heapq` and tuples break ties
  differently); every expression in the same order, without fast math; the returned dicts rebuilt in today's key
  order by a small Python step; the `WAITING LINK` print, the `study_area` check and the negative-cost guard in a
  Python wrapper.
- Estimate (not measured): the function 4-8x faster with the dict rebuilding, the run from about 5 to about 3 min.
- Cost: a second, compiled copy of the fare rules (every fare change must be made there too; harder to read and
  debug), a new dependency, 5-10 s of compile time per run (unless cached), and several steps, each with an
  equivalence test against the current function and a full run (`REPRODUCED`).
- Most worth it if the model is run many times, for example inside the Bayesian optimizer.

---

## Continuing work in a fresh clone

1. Clone: `git clone https://github.com/ritunuci/Multimodal_Transportation_System_Model` (for example in `D:\Ritun`).
2. Set the author **in the clone**:
   `git config user.name "Ritun Saha"` and `git config user.email "ritunsaha95@gmail.com"`.
3. Python: the `fleetpy` conda env (`C:\Users\Autonomicity\.conda\envs\fleetpy\python.exe`; in VS Code:
   *Python: Select Interpreter*). Gurobi with a valid license must be installed (used by repositioning).
4. Check that everything is in place: `python tools/check_inputs.py` must report that all frozen inputs match.
5. Optional full check (about 5–7 min): `python run_examples_new_parking.py`, then `python tools/compare_reference.py`, which must print
   `REPRODUCED`. To also log every file the run opens or changes (the I/O tracer):
   `python tools/trace_run.py run_examples_new_parking.py <log.tsv>`. The order matters: script first, then the log;
   the other order overwrites the script.
6. Working rules:
   - After **any** code change, do a full run with the reference inputs and seed; `compare_reference.py` must print `REPRODUCED`
     (unless the change is meant to change results, in which case make and document a new reference).
   - Keep source files in CRLF.
   - Do not edit the frozen inputs in `mtsm_data/` without recording it here and regenerating `mtsm_data/MANIFEST.csv`
     (`python tools/check_inputs.py --write`).
   - Change parameters in a copy of `mtsm_data/input_parameter/mtsm_constant_configurations.csv` and run with
     `--config <copy>`; the frozen file holds the reference values.
   - `fleetpy/` is upstream FleetPy: do not change it without recording the change in `fleetpy/LOCAL_CHANGES.md`. Inputs
     the model gives FleetPy belong in `mtsm_data/lemon_grove/fleetpy_inputs/` (copied in by `fleetpy_runner.py`).
     Files restored from upstream keep upstream's LF line endings.
7. The old folder `D:\Ritun\Siwei_Micro_Transit\FleetPy_SanDiego` is an archive; the old data folders
   (`Bayesian_Optimization`, `Data\0719_input`, `Ritun\Lemon Grove`) are no longer needed by the code.
8. A new Claude Code session does not know the earlier conversation. Start it with: *"Read docs/progress.md and
   docs/reference_results/README.md."*

---

## Open questions / to check (Phase 4)
- ~~`M_trips = 0`, `M_VMT = 0`, `cnvrg = 0`, `tt_mob_lgsm_inc_with_micro = 0`~~: not a bug. Those values were read from
  row 1 (the fixed-route-only baseline). Row 3 has normal values (corrected 2026-10-23).
- Rows 1 and 2 of the evaluation CSV are identical `FRT_only_scen` rows. Is the duplicate intended?
- `FRT_headway = 20` would overwrite a frozen input. `update_initial_net_with_bayesian_headway()` writes
  `initial_super_network_non_micro_hw_{headway}.csv` into `mtsm_data/lemon_grove/initial_network/`, and for headway 20 that is the frozen
  `initial_super_network_non_micro_hw_20.csv` (the fixed-route network at the base headway). This predates our changes.
  The startup check would report the file as changed afterwards. To decide: is the overwrite intended, or should
  the rebuilt file get its own name?
- **`hw_20_virstop_100` network: checked 2026-10-23, no effect on current results.**
  - `output_performance_metrics.create_nodes_emp_dict()` hard-codes `headway = 20`, `virstop = 100` and the
    `Data\0719_input\lemon_grove\initial_network` folder (lines 241, 247–251). It reads the network file only to collect
    the **set of node IDs**. Nodes with no assigned employment then get 0 employment (line 329). The function is called from
    the accessibility calculations (lines 614, 645, 1113), which feed the `wghted_acc_emp_{5,10,15}_min` columns.
  - This file dates from 2023-12-24. It has the **same 2269 nodes** as the network the scenario actually uses
    (`initial_super_network_micro_hw_10_virstop_75.csv`). It has 568 extra virtual-stop links, but their travel times and
    links are never used. So the employment values are the same either way.
  - Remaining risk: if a future scenario has a different node set, the accessibility numbers would be silently wrong.
    (Since Phase 1b the file is a frozen, checksummed input in `mtsm_data/lemon_grove/initial_network_0719/`, so it can no
    longer change unnoticed.) Fix later: take the node list from the network the scenario actually uses.
- ~~`output_performance_metrics.py` reads `pre_nodes.csv`, `final_land_use.csv`, the ActivitySim MGRA files and the
  node→MGRA mapping from outside the codebase~~: done in Phase 1b. They are frozen inputs in `mtsm_data/`.

## Backups and working files
- Copy of every folder the run modifies, taken before the first traced run (2026-10-22):
  `C:\Users\Autonomicity\AppData\Local\Temp\claude\d--Ritun-Siwei-Micro-Transit-FleetPy-SanDiego\4996e5fe-e9cb-4dfa-bfda-0aa05bccaa66\scratchpad\backup_pre_run`.
  This is a temp folder; copy it somewhere permanent if it is needed long term.
- The same scratchpad folder holds the I/O traces (`io_trace.tsv`, `io_trace_callers.tsv` with calling lines,
  `io_trace_mtsm.tsv` from the restructured run), the output sets of each test run (`out_*`) and the helper scripts:
  `trace_run.py` (copied to `tools/trace_run.py` on 2026-11-11) / `trace_run_callers.py` (I/O tracing), `snapshot_outputs.py`, `compare_runs.py`.
  The byte-for-byte comparison now lives in the repo as `tools/compare_reference.py`.
- `Bayesian_Optimization\Input_parameter\input_parameter.csv.bak_before_seed`: the parameter file before the
  `random_seed` column was added (Phase 1).
