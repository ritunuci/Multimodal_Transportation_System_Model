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
| I-07 | `docs/progress.md` plan table is out of date | Low | Open | 2026-11-07 |
| I-08 | FleetPy's `README.md` still installs from `requirements.txt` | Low | Open | 2026-10-23 |

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
- **What:** `test_file_backup_latest.py` writes each candidate's values into
  `mtsm/input_parameter/input_parameter.csv`, which is a frozen, checksummed input. After a session the file holds the
  last candidate's values.
- **Impact:** after an optimizer session, `tools/check_inputs.py` and the model's startup check report the file as
  changed, and `tools/compare_reference.py` does not print `REPRODUCED` until the reference values are restored (they
  are listed in `docs/reference_results/README.md`). Nothing records which parameters produced the files in
  `mtsm/lemon_grove/output/`.
- **Fix:** Phase 3. Give each run its own parameter file and output folder, and record the parameters in a
  `run_manifest.json`. Until then, restore the file with `git checkout mtsm/input_parameter/input_parameter.csv` after
  each optimizer session.

### I-03: The optimizer has not been run since the changes
- **Status:** Open. **Severity:** Medium. **Found:** 2026-10-23 (Phases 1c and 2b).
- **What:** `test_file_backup_latest.py` was changed three times: the `mtsm/` paths (`d5aee47`), launching the model
  with `sys.executable` (`da839b0`), and stopping on a failed model run (`09e0684`). Each change compiles, and the
  failure handling was tested against a fake model process. The optimizer itself was never run, because a session
  takes many model evaluations, overwrites the parameter file (I-02) and needs Gurobi (I-01).
- **Impact:** an error in the optimizer's own code would only show up in the first real session.
- **Fix:** after I-01 is fixed, run a short session (a few candidates) into a throwaway `folder_name`. Check that
  `per_call_results.csv` matches the evaluation files, that a deliberately failed run stops the optimizer, and then
  restore the parameter file (I-02).

### I-04: Rows 1 and 2 of the evaluation CSV are identical
- **Status:** Decision needed. **Severity:** Medium. **Found:** 2026-10-23 (Phase 1).
- **What:** `mtsm/lemon_grove/output/lemon_grove_evaluation_zonal_partition_False.csv` has 3 data rows. Rows 1 and 2
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
  `initial_super_network_non_micro_hw_{headway}.csv` into `mtsm/lemon_grove/initial_network/`. For headway 20 this is
  the frozen `initial_super_network_non_micro_hw_20.csv` (the fixed-route network at the base headway).
- **Impact:** a run or optimizer candidate with headway 20 changes a frozen input. The startup check and
  `tools/check_inputs.py` would then report it as changed, and later runs would read the rebuilt file instead of the
  original.
- **To decide:** is the overwrite intended? If not, give the rebuilt file its own name, or stop the run before it
  overwrites a frozen file.

### I-06: Accessibility uses a hard-coded network for its node list
- **Status:** Open. **Severity:** Medium. **Found:** 2026-10-23 (Phase 4 check).
- **What:** `create_nodes_emp_dict()` (`output_performance_metrics.py`) hard-codes `headway = 20` and `virstop = 100`
  and reads `mtsm/lemon_grove/initial_network_0719/initial_super_network_micro_hw_20_virstop_100.csv`, only to collect
  the set of node IDs. Nodes with no assigned employment get 0. The result feeds the `wghted_acc_emp_{5,10,15}_min`
  columns.
- **Impact:** none today. The file has the same 2269 nodes as the network the scenario uses
  (`initial_super_network_micro_hw_10_virstop_75.csv`). A future scenario with a different node set would get
  silently wrong accessibility numbers.
- **Fix:** take the node list from the network the scenario actually uses. If the node set is unchanged, the reference
  still reproduces; check with a full run and `compare_reference.py`.

### I-07: `docs/progress.md` plan table is out of date
- **Status:** Open. **Severity:** Low. **Found:** 2026-11-07.
- **What:** the Phase 2 row says "Tag + push to do". The push is done (`65861ec` is on `origin/main`), and the user
  decided not to add a `v2-env-locked` tag for now. Step 6 of the Phase 2b plan also still mentions the tag.
- **Fix:** update the row and step 6 at the next edit of `docs/progress.md`.

### I-08: FleetPy's `README.md` still installs from `requirements.txt`
- **Status:** Open. **Severity:** Low. **Found:** 2026-10-23 (Phase 2b, step 2).
- **What:** `requirements.txt` is now only a comment pointing to `env/`, but FleetPy's `README.md` still says
  `conda install --file requirements.txt`, which now installs nothing.
- **Fix:** point that section of `README.md` to `env/README.md`.

---

## Closed

None yet.
