# Reproducibility work: progress log

Goal: make the results we report for the research reproducible, and make the codebase self-contained (no
dependency on any folder outside `FleetPy_SanDiego`). Study area: **Lemon Grove only**.
Reported results: `mtsm/lemon_grove/output/`. Before 2026-10-23 they were written to
`D:\Ritun\Siwei_Micro_Transit\Bayesian_Optimization\lemon_grove\output_folder\`.
Entry point: `run_examples_new_parking.py`, run in the `fleetpy` conda env
(`C:\Users\Autonomicity\.conda\envs\fleetpy`, Python 3.10.19).

Newest entries go at the bottom of each phase. In the "Baseline findings" section, paths are relative to
`D:\Ritun\Siwei_Micro_Transit\` (the locations before `mtsm/`). Elsewhere they are relative to the codebase root.

---

## Plan overview

| Phase | What | Status |
|---|---|---|
| 1 | Make a single run deterministic: seed, hash seed, PYTHONPATH, Gurobi check | Done, verified 2026-10-23 |
| 1b | Self-contained codebase: frozen, checksummed inputs and all outputs under `mtsm/` (former step 2.3); reference results; guard for unsupported configurations | Done, verified 2026-10-23 |
| 1c | Optimizer (`test_file_backup_latest.py`) reads and writes `mtsm/` instead of outside folders | Done 2026-10-23 (compiled, not run) |
| 2 | Freeze code (git: two-step commit, then GitHub repo) and environment (conda export, lock files) | Git part done 2026-10-23 (see Phase 2a); environment lock to do |
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
- The optimizer is **`test_file_backup_latest.py`** (codebase root). `New folder/MOBO_for_micro.py` is an older
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

## Phase 1b: self-contained codebase (`mtsm/`)

### Layout (2026-10-23)
Each folder outside the codebase that the run used now has exactly one folder in `mtsm/`. No folder was split and no
file was renamed, so the code still builds the same file names. The folder constants are in `mtsm_paths.py`
(imported as `mtsm`). They are derived from the location of that file, so the codebase still works if it is moved.

| `mtsm/` folder | Former location (under `D:\Ritun\Siwei_Micro_Transit\`) | Contents |
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

- **Frozen inputs:** 14 files, copied unchanged. `mtsm/MANIFEST.csv` holds path, size, SHA-256 and role.
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
  - **Output folders** in `mtsm/` are created if missing, since git does not keep empty folders.
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
  `ERROR: configuration ... is not self-contained (mtsm/) yet: test_area=['downtown_sd'] (only lemon_grove), debug_mode_list=True`
  and exit code 1. The parameter file was restored afterwards, and `check_inputs.py` passes.

### Optimizer note
- Addressed in Phase 1c, for the actual optimizer `test_file_backup_latest.py`.

---

## Phase 1c: optimizer reads and writes `mtsm/`

### Changes (2026-10-23), `test_file_backup_latest.py`
| What | Before | Now |
|---|---|---|
| Parameter file (read + written each call) | `Bayesian_Optimization/Input_parameter/input_parameter.csv` | `mtsm/input_parameter/input_parameter.csv` |
| Evaluation file (read) | `Bayesian_Optimization/lemon_grove/output_folder/lemon_grove_evaluation_zonal_partition_False.csv` | `mtsm/lemon_grove/output/` (same name) |
| Individual results (read) | `Bayesian_Optimization/lemon_grove/output_folder/individual_results_micro_M_…_scen_10.csv` | `mtsm/lemon_grove/output/` (same name) |
| Optimizer outputs (`per_call_results.csv`, `run_log.txt`, `indv_res/`, `per_itr_agg_sim_output/`, result CSVs, `indiv_call_timings_eval.csv`) | `Bayesian_Optimization/optimization_output/<folder_name>/` | `mtsm/lemon_grove/optimization_output/<folder_name>/` (`folder_name` is still `LG_submission_results_R2`) |
| Model launch | `run_examples_new_parking.py`, relative to the current working directory | absolute path in the codebase, `cwd` set to the codebase root, so the optimizer works from any working directory |

- New constant `mtsm_paths.LG_OPTIMIZATION_OUTPUT_DIR`. The script imports `mtsm_paths as mtsm`.
- Unchanged: the model's Python interpreter `C:/Users/Autonomicity/.conda/envs/fleetpy/python` (the environment is
  outside the codebase by nature; see Phase 2), all optimizer logic, column indices and file names.
- `New folder/MOBO_for_micro.py`: kept unchanged. It still points to the old folders.
- Earlier optimizer results in `Bayesian_Optimization/optimization_output/` were **not** moved. New optimizer runs start in
  `mtsm/lemon_grove/optimization_output/`.

### Verification
- The script compiles, CRLF line endings are kept, and no `D:/` path is left outside comments. **Not run.** A run takes many
  model evaluations and overwrites the parameter file.

### Consequence to keep in mind
- The optimizer overwrites `mtsm/input_parameter/input_parameter.csv`, which is a frozen input. After an optimizer
  session, the parameter file holds the last candidate's values. `tools/check_inputs.py` and the model's startup check will
  then report it as changed, and `tools/compare_reference.py` will not reproduce until the reference parameters are restored
  (they are listed in `docs/reference_results/README.md`). Long-term fix (Phase 3): give each run its own parameter
  file instead of editing the frozen one.
- `mtsm/lemon_grove/optimization_output/` is generated and git-ignored (Phase 2a).

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
  - `run_examples_new_parking.py` came back to exactly 2204 lines and `test_file_backup_latest.py` to 640, as
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
  `mtsm/lemon_grove/{output,final_network,indiv_output,optimization_output}/` (the folders stay via `.gitkeep`), and the networks
  rebuilt every run in `mtsm/lemon_grove/initial_network*/`. Exceptions keep the two frozen networks
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
   - Do not edit the frozen inputs in `mtsm/` without recording it here and regenerating `mtsm/MANIFEST.csv`
     (`python tools/check_inputs.py --write`).
   - The optimizer (`test_file_backup_latest.py`) overwrites `mtsm/input_parameter/input_parameter.csv` (see Phase 1c).
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
  `initial_super_network_non_micro_hw_{headway}.csv` into `mtsm/lemon_grove/initial_network/`, and for headway 20 that is the frozen
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
    (Since Phase 1b the file is a frozen, checksummed input in `mtsm/lemon_grove/initial_network_0719/`, so it can no
    longer change unnoticed.) Fix later: take the node list from the network the scenario actually uses.
- ~~`output_performance_metrics.py` reads `pre_nodes.csv`, `final_land_use.csv`, the ActivitySim MGRA files and the
  node→MGRA mapping from outside the codebase~~: done in Phase 1b. They are frozen inputs in `mtsm/`.

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
