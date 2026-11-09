# Plan: restructure the entry script (`run_examples_new_parking.py`)

Status: **in progress.** The user's decisions are recorded under "Decisions" (2026-11-09). Steps 1 to 3 are done
(see "Steps"). The starting point was commit `92ae5fa`; line numbers below refer to it unless stated otherwise.

## Why

`run_examples_new_parking.py` is 1,921 lines. Almost all of it is one block under `if __name__ == "__main__":`, nested
up to 18 levels deep. It is hard to read for four reasons:

- **No functions.** Everything shares about 150 loose variables, among them about 70 per-scenario dictionaries
  (`agent_O`, `ag_VMT_F`, `off_micro_*`, ...).
- **Repeated code.** The split of a path into walk / microtransit / fixed-route legs is written three times, and the
  writing of the individual-results file twice.
- **Code that never runs.** Unused scenario types, debug switches, FleetPy's old example branch, and much
  commented-out code.
- **Results exist only as file rows.** There is no data structure for them.

## What the script does now

| Lines | Content |
|---|---|
| 72–150 | Restart with `PYTHONHASHSEED=0`; read `input_parameter.csv`; startup check; random seeds |
| 150–220 | About 25 settings and constants (costs, thresholds, operating periods) |
| 221–310 | Per study area: folders, transit lines, node mapping, networks, travelers. The evaluation file is opened here and stays open for the rest of the run |
| 311–380 | Seven nested scenario loops: repositioning × fare scenario × headway × virtual stops × fleet × operating periods × microtransit setup. Each list has one element in practice |
| 387–497 | About 70 per-scenario dictionaries are set up |
| 498–1200 | The iteration loop (`while not converged`). For each traveler: pick the network for the time period; find the auto, FRT-only and with-microtransit paths; costs, logit probabilities, logsums; one random draw; split the chosen path into legs; write the FleetPy and FRT demand rows |
| 1202–1734 | Convergence test. After convergence: operating costs, subsidies, accessibility, individual-results files, evaluation rows (FRT-only base case and the scenario) |
| 1735–1865 | If not converged: run FleetPy, update the networks, read the rejection rate |
| 1866–1921 | FleetPy's old example branch (`test_repositioning=True`), never taken |

## Proposed architecture

A small package for the model, with a thin entry script:

```
run_examples_new_parking.py      thin entry: restart with hash seed, read config, run_model(config)  (~50 lines)
mtsm_model/
  config.py        read input_parameter.csv -> RunConfig (dataclass); startup check; the model constants
                   in one place, named and commented (costs, thresholds, periods)
  scenarios.py     the scenario loop -> one Scenario object per scenario (headway, fleet, fares, file names, ...)
  state.py         dataclasses replacing the ~70 loose dicts: TravelerState (per traveler), IterationTotals,
                   BaseCase (the FRT-only "without microtransit" results)
  networks.py      load the initial / final super-networks per iteration; pick a traveler's network by period
  paths.py         per traveler: auto, FRT-only and with-microtransit least-cost paths, including the caching
                   of the base-case paths in the first fare scenario
  choice.py        costs (incl. parking), binary-logit probabilities, logsums, the mode draw, mode-change threshold
  trip_legs.py     split a path into walk / microtransit / FRT legs (times, distances, VMT, waits) - written once,
                   used by the three places that repeat it today
  iteration.py     one iteration: loop over travelers, write the FleetPy + FRT demand files -> IterationTotals
  microtransit.py  run FleetPy (through fleetpy_runner), update the networks, read the rejection rate
  results.py       after convergence: operating costs, subsidies, accessibility, individual results, evaluation rows
  model.py         run_model(): scenario loop -> iterate until converged -> results
```

- The existing helper modules stay where they are at first: `network_algorithms.py`, `binary_choice.py`,
  `convergence_test.py`, `update_network_files.py`, `output_performance_metrics.py`, `update_initial_network.py` and
  `fleetpy_runner.py`. Moving them into the package can be a later step.
- `mtsm_paths.py` stays, imported as `mtsm`. The package is therefore not named `mtsm/`, which would clash with
  that import name.

The top level should read like the framework diagram (`docs/mtsm_framework.png`):

```python
for scenario in scenarios(config):
    state = initial_state(...)
    while not converged:
        totals = run_iteration(scenario, state, networks)        # choice model for all travelers
        converged = check_convergence(state, iteration)
        if not converged:
            networks = update_microtransit(scenario, iteration)  # FleetPy -> super-network
    write_results(scenario, state, totals, eval_writer)
```

## How to restructure without changing any result

The rule stays: after every step, a full seed-0 run must print `REPRODUCED` (all 32 reference files byte-identical,
`docs/reference_results/`). Specific to this work:

1. **Small steps, each verified and committed on its own.** A step only moves code into functions, unchanged in
   what it computes.
2. **Keep the order of everything that affects the bytes of the outputs:**
   - **Travelers in the same order.** The model makes one random draw, `random.random()` (line 799), per traveler
     per iteration. The individual-results files record each draw, so the reference checks this.
   - **Dictionary insertion order**, which decides the row order in the output files.
   - **The order of floating-point operations.** For example, `(a + b + c) / 3` must not become `sum(...) / 3`.
   - **The point at which FleetPy is called.** FleetPy re-seeds the random generators in the same process.
3. **Values carried over from an earlier pass, the biggest hidden risk.** Some variables are set only in some
   branches. The code may then read a value left over from the previous traveler or iteration, for example in the
   `micro_only` branches. In a function, that value would disappear and the result would change.
   **Mitigation:** before extracting a block, list with Python's `ast` module every variable the block reads but
   does not set. Each one becomes an explicit input, or is reported to the user if it is a carried-over value.
4. **Repeated code is merged only if the copies are identical.** Where the three leg-split copies differ, the
   differences become parameters. They are not "fixed".
5. **No behavior changes inside the restructuring.** Anything that looks like a bug is recorded as an open issue
   (`docs/open_issues.md`) instead of being fixed along the way.

## Must be kept

- **Lines 1738–1764 of `run_examples_new_parking.py` (as of commit `92ae5fa`):** the commented-out block
  "Ritun added", which adds synthetic microtransit demand before FleetPy runs (`syn_rq`, local agents, 3 extra
  requests per microtransit traveler, rq ids from 60000). The user needs it. It stays as commented-out code. It
  moves with the FleetPy step (planned `microtransit.py`) to the same position, just before FleetPy is run,
  unchanged.
- **Its import must stay too,** although nothing active uses it:
  `from pre_process.generate_demand_files import synthesize_requests_with_trend_time as syn_rq`.
  It moves along with the block.

## Steps

Each step ends with a full run (`REPRODUCED`), a stop for the user's review, and a commit message. A run takes about
30 minutes.

1. **Remove code that never runs** (depends on decision 1), and the commented-out code, except the block under "Must
   be kept". Git keeps the history. **Done 2026-11-09** (`REPRODUCED`):
   - removed `test_repositioning` with FleetPy's old example branch, `iteration_debug`, `zonal_partition` (also as
     parameters of the helper functions; the evaluation file keeps the name `..._zonal_partition_False.csv`, which
     the optimizer reads), and the commented-out code of the entry script, plus the commented-out
     `indiv_convergence_test_binary_choice` in `convergence_test.py`;
   - kept and commented the aggregate convergence test (`indiv_converg_test`, `convergence_test()`), which is
     unfinished (`docs/open_issues.md`, I-16);
   - kept `micro_only` and `non_micro`;
   - kept the block under "Must be kept" and its import. It is now 4 spaces less indented, like the code
     around it, because the `if test_repositioning==False:` around the whole run was removed (lines 1553-1579
     after step 1);
   - the helper modules' `__main__` test harnesses and their commented-out code were not changed; the
     standalone scripts were not changed (they still call the old signatures; nothing runs them).
2. **Config and constants** → `config.py`. **Done 2026-11-09** (`REPRODUCED`):
   - new package `mtsm_model/` with `config.py`: `RunConfig` (the parameters of `input_parameter.csv`; same reading
     code as before: the lists take every row, the other fields the last row), `read_run_config()`,
     `check_run_config()` (the startup check, the frozen-input check, the output folders), `str2bool()`, and the
     fixed settings and constants as commented module constants;
   - the entry script uses `cfg.<name>` for input parameters and `config.<NAME>` for constants (the old variable
     names, constants in upper case; renamed by token, so strings and keyword arguments are unchanged).
     `headway_scenarios = [cfg.headway]` and `fleet_size_scenarios = cfg.read_fleet_size` stay in the entry script,
     because `headway` and `fleet_size` are loop variables there;
   - constants still written as numbers inside the code (operating costs $170/h and $130/h, the time-period
     limits, the microtransit node offset 1171, the parking charge factors) move to `config.py` together with the
     code that uses them (steps 4-7), so that each step changes one part of the script.
3. **State dataclasses** → `state.py`. This is a mechanical rename of the dictionaries
   (`agent_O[rq_id]` → `state.agent_O[rq_id]`): the same objects, the same order. **Done 2026-11-09** (`REPRODUCED`):
   - `TravelerState` (`state`): the per-traveler dicts (`agent_*`, `ag_*`, `pre_iter_*`, the deltas), created once
     per scenario where they were initialized before; `BaseCase` (`base`): the `off_micro_*` values of the
     fixed-route-only base case; `IterationTotals` (`totals`): the counts and VMT totals reset at the start of each
     iteration (`num_*`, `pure_*_user`, `M_F_user`, `VMT_*`);
   - each name was bound only at its initialization (checked before the change; the one other assignment,
     `num_transit_users = ...`, became `totals.num_transit_users = ...`), so the rename does not change what is
     read where;
   - the iteration control and history (`iteration`, `converged`, `rejection_rate`, `iter_agent_choice_prob`,
     `iter_sum_sq_per_diff`, ...) and `transit_tt_VMT` stay local; they move with the iteration loop (step 6) and
     the results (step 7);
   - `off_micro_c_tt_travel_time` and `off_micro_f_tt_travel_time` are created but never filled (their uses were
     commented out); kept as fields for now, marked "not filled".
4. **Trip legs** → `trip_legs.py`, removing the three copies.
5. **Paths and choice** → `paths.py`, `choice.py`.
6. **One iteration** → `iteration.py`; the FleetPy step → `microtransit.py`, together with the kept block.
7. **Results after convergence** → `results.py`.
8. **Scenario loop and `run_model`** → `scenarios.py`, `model.py`. The entry script shrinks to about 50 lines.
9. **Docs:** `progress.md`, the README layout table, a short code map in the README.

## Decisions (2026-11-09)

1. Remove `test_repositioning`, `iteration_debug`, the `zonal_partition` branches and the commented-out code (except
   the block under "Must be kept"). **Keep the aggregate convergence test** (`indiv_converg_test == False`), with
   enough comments to understand it later. **Keep `micro_only` and `non_micro` as options.**
2. (a) Keep the ability to run several scenarios in one run.
3. Keep the name `run_examples_new_parking.py` for now.
4. Package name `mtsm_model/`.

Correction to the question below: `non_micro` is not only a scenario type. `initial_super_network["non_micro"]`
is the fixed-route-only network used for every traveler's "without microtransit" path, and the results switch to
`"non_micro"` to write the fixed-route-only base case. It could not have been removed.

## Decisions needed (as asked)

1. **Which branches that never run are removed in step 1?**
   - **Recommended to remove:**
     - `test_repositioning` (FleetPy's old example);
     - `iteration_debug`;
     - the aggregate convergence test (`indiv_converg_test == False`);
     - the `zonal_partition` branches;
     - the commented-out code (except the block under "Must be kept").
   - **To decide: the scenario types `micro_only` and `non_micro`.** They are model options, but the run never uses
     them, and `micro_only` has the downtown San Diego node limit (I-13). Remove them, or keep them as supported
     options? Keeping them makes the restructuring larger and riskier, because that is where the carried-over values
     are.
2. **Scenario loops with one element each:**
   - (a) keep the ability to run several scenarios in one run: a clean scenario loop in `scenarios.py`
     (recommended, unless multi-scenario runs are known not to be needed; the "first fare scenario" path caching
     exists only for them); or
   - (b) one scenario per run, which is how the optimizer uses the model, and simpler.
3. **Name of the entry script.** The optimizer starts the model as `run_examples_new_parking.py`. Recommended:
   keep the name for now. Renaming it (for example to `run_model.py`) means also changing the optimizer's launch
   line.
4. **Package name:** `mtsm_model/`, or another name?
