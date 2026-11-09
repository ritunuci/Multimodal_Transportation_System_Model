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
| 2c | FleetPy as a separate module: `fleetpy/`, `fleetpy_runner.py`, inputs copied from `mtsm_data/` | In progress: steps 1-2 done 2026-11-07 |
| 2d | Remove downtown San Diego: code (also commented), inputs and outputs | In progress: steps 0-2 done 2026-11-08 |
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
  3. Give the model its own vehicle type (capacity 8), with a checked reference update (I-09).
  4. Restore FleetPy's example data, archive the downtown San Diego data, run FleetPy's own example (I-10).
  5. Docs.
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
- Checks: compiles; pyflakes reports no new warnings; CRLF kept.
- Verification (2026-11-08): passed. Full seed-0 run under the I/O tracer: `compare_reference.py` **32 identical,
  `REPRODUCED`**; `check_inputs.py` passes; no generated files in `git status`.

---

## Continuing work in a fresh clone

1. Clone: `git clone https://github.uci.edu/rituns/Multimodal_Transportation_System_Model` (for example in `D:\Ritun`).
2. Set the author **in the clone**:
   `git config user.name "Ritun Saha"` and `git config user.email "rituns@uci.edu"`.
3. Python: the `fleetpy` conda env (`C:\Users\Autonomicity\.conda\envs\fleetpy\python.exe`; in VS Code:
   *Python: Select Interpreter*). Gurobi with a valid license must be installed (used by repositioning).
4. Check that everything is in place: `python tools/check_inputs.py` must report that all frozen inputs match.
5. Optional full check (about 30 min): `python run_examples_new_parking.py`, then `python tools/compare_reference.py`, which must print
   `REPRODUCED`.
6. Working rules:
   - After **any** code change, do a full run with the reference inputs and seed; `compare_reference.py` must print `REPRODUCED`
     (unless the change is meant to change results, in which case make and document a new reference).
   - Keep source files in CRLF.
   - Do not edit the frozen inputs in `mtsm_data/` without recording it here and regenerating `mtsm_data/MANIFEST.csv`
     (`python tools/check_inputs.py --write`).
   - The optimizer (`Bayesian_optimization_script.py`) overwrites `mtsm_data/input_parameter/input_parameter.csv` (see Phase 1c).
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
  `trace_run.py` / `trace_run_callers.py` (I/O tracing), `snapshot_outputs.py`, `compare_runs.py`.
  The byte-for-byte comparison now lives in the repo as `tools/compare_reference.py`.
- `Bayesian_Optimization\Input_parameter\input_parameter.csv.bak_before_seed`: the parameter file before the
  `random_seed` column was added (Phase 1).
