# Plan: MTSM for any study area, with Lemon Grove as the example

Status: **decisions made 2026-11-24** (section "Decisions (user, 2026-11-24)" at the end; it overrides the plan text
where they differ). Step A, removing the accessibility calculation, comes before Phase 0. Written 2026-11-23, against
commit `d61005a`; line numbers refer to that state.

## The user's request (2026-11-23)

- The repository runs only for Lemon Grove. It is to be general: a user who picks up the repository can set up their
  own study area by supplying the **required input**.
- The repository ships the current Lemon Grove implementation as the example.

## Ground rules for this work

- Restructuring and new input data are kept apart.
  - Phases 1-4 change only how the code finds and checks its inputs. Lemon Grove must stay byte-identical: every step
    ends with a full seed-0 run and `tools/compare_reference.py` printing `REPRODUCED` (32 files).
  - A step that changes Lemon Grove's results is done only on the user's decision, as its own documented reference
    update (like I-21) or in the batched new reference.
- The new road, FRT and period networks (I-33, I-34, I-35) and the result-changing fixes waiting for a new reference
  (I-19, I-22, I-24, I-25) come after Phases 0-4. They then arrive as inputs in the format this plan defines.

## What ties the repository to Lemon Grove today

1. **Paths.** `mtsm_paths.py` defines only Lemon Grove folders (`LG_*`). They are used in:
   - `mtsm_model/helpers/folder_directory.py`, `update_network_files.py`, `update_initial_network.py`,
     `output_performance_metrics.py`, `get_microtransit_skims.py`, `fleetpy_runner.py`;
   - `tools/check_inputs.py` and `tools/compare_reference.py` (reference name `lemon_grove_seed0`);
   - the optimizer, whose output folder `LG_submission_results_R2` is fixed (`Bayesian_optimization_script.py:79`).
2. **`if study_area == "lemon_grove"` branches.** For any other area these leave a value unset or skip work:
   - the FRT fare and the microtransit start fare (`network_algorithms.py:352`, `:372`): $0 elsewhere (I-34, item 2);
   - the microtransit waiting-time update (`update_network_files.py:340`): stays at 180 s elsewhere (I-34, item 6);
   - FRT line length, duration, VMT and ridership (`output_performance_metrics.py`): `UnboundLocalError` elsewhere
     (I-34, item 1);
   - the accessibility code (`output_performance_metrics.py`);
   - `config.check_run_config` rejects any other area (`config.py:249`).
3. **File names that contain the area.**
   - `base_super_network_lemon_grove_micro_hw_10_virstop_75.csv`, `base_super_network_lemon_grove_non_micro_hw_10.csv`
     (`update_initial_network.py`).
   - FleetPy: `lemon_grove_example_network`, `lemon_grove_example_demand`, vehicle type `lemon_grove_vehtype`
     (`fleetpy_runner.LG_STAGED_INPUTS`, `fleetpy_runner.py:251`, `:264`).
   - About 25 FleetPy scenario files, one per fleet size and repositioning setting; the run uses 2.
4. **Area facts in the shared parameter file.** `num_walk_nodes` (1099), `microtransit_node_offset` (1171) and
   `micro_only_max_walk_node` (731, downtown San Diego's value; I-13) are in
   `mtsm_data/input_parameter/mtsm_constant_configurations.csv`, next to model parameters that hold for any area.
5. **Hard-coded choices.**
   - The accessibility node list comes from a fixed `hw_20_virstop_100` network in `initial_network_0719/` (I-06).
   - A run with headway 20 overwrites a frozen input (I-05).
   - The FRT line length is the sum of a route's *unique* link distances, which is right only for the old FRT network
     (I-34, item 1).
6. **SANDAG-specific zone data.**
   - `mtsm_data/region/final_land_use.csv`: about 23,000 SANDAG MGRA rows; the code uses `zone_id` and `TOTEMP`.
   - `region/activitysim_output/lemon_grove_MGRA_pop_inc.csv` (population, income per MGRA),
     `lemon_grove_MGRA_adj.csv` (adjacent MGRAs for MGRAs with no node), and
     `lemon_grove/transit/mgra_node_mapping/Nodes_MGRA_mapping.csv` (node -> MGRA).
7. **New finding (2026-11-23): the Lemon Grove accessibility reads downtown San Diego's node file.**
   - `get_fleetpy_demand_nodes()` (`output_performance_metrics.py:176`) reads `mtsm_data/region/pre_nodes.csv`. That
     file has 732 nodes (0-731, 497 demand nodes), narrower coordinates than Lemon Grove's, and the node range of
     downtown San Diego (its last walk node is 731).
   - Lemon Grove's own file, `mtsm_data/lemon_grove/transit/network_folder/pre_nodes.csv`, has 1,099 nodes (814
     demand nodes).
   - The result is used in `create_nodes_emp_dict` (which nodes get employment) and as the origins of the accessibility
     calculations (`output_performance_metrics.py:378`, `:561`). Of the 1,062 nodes in Lemon Grove's node -> MGRA
     mapping, 483 are demand nodes in the downtown file and 805 in Lemon Grove's.
   - Effect: the `wghted_acc_emp_5/10/15_min` values (and the per-zone accessibility file) are computed over the wrong
     node set. Fixing it changes these reported values. Not yet in `docs/open_issues.md` (proposed: I-37; decision 6).
8. **FleetPy inputs.** `fleetpy_runner.LG_STAGED_INPUTS` is a fixed list of Lemon Grove files. The initial vehicle
   positions (`imbalanced.csv`) are Lemon Grove's and need a review anyway (I-36).

## The phases

### Phase 0: input specification (docs only)

Write `docs/study_area_inputs.md`, the contract between a user and the model. For each input:

- file name and place in `mtsm_data/<area>/`, columns, units, coordinate system, required or optional;
- which other files the builder or the run derives from it;
- the Lemon Grove file as the worked example.

It also states the rules that tie the inputs together:

- node numbering: walk node i = FleetPy node i = microtransit node `microtransit_node_offset` + i; the FRT stop nodes
  lie between the last walk node and the first microtransit node;
- every trip origin and destination is a walk node; every FRT stop is joined to a walk node;
- the road network that FleetPy uses has the same nodes as the walk network.

The rest of the work follows from this file, so it comes first. If decision 8 is "now", it also defines networks per
time period (I-35).

### Phase 1: per-area paths (Lemon Grove reproduces)

- `mtsm_paths.py`: replace the `LG_*` constants with a function, e.g. `area_paths(area)`, that returns every folder
  of `mtsm_data/<area>/` (demand, networks, transit, zones, FleetPy inputs, outputs).
- Use it everywhere listed in item 1, including `tools/check_inputs.py`, `tools/compare_reference.py` (reference
  names `<area>_seed0`) and the optimizer (output folder under the area).
- Fixed, generic file names inside the area folder (decision 4). The names FleetPy writes into its outputs
  (`<area>_example_network`, `<area>_vehtype`) keep their form, so the FleetPy reference files stay byte-identical.
- `mtsm_data/MANIFEST.csv` is rewritten for any renamed frozen input.

### Phase 2: no more Lemon Grove branches (Lemon Grove reproduces)

- Fares, the microtransit waiting-time update, the metric paths and the accessibility code run for every area.
- Remove the "only lemon_grove" startup check.
- Node counts: derived from the network files, or kept as parameters and checked against them (decision 3).
- I-13: the `micro_only` branch uses the area's own last walk node.

### Phase 3: area-neutral calculations

- I-06: the accessibility node list comes from the network the scenario uses. Same node set for Lemon Grove, so it
  should reproduce.
- FRT line length and number of stops come from a route table supplied with the FRT inputs (e.g. `frt_routes.csv`:
  `route, length_m, num_stops`). Lemon Grove's table is written from today's calculation, so Lemon Grove reproduces.
  The ABM3 networks (I-34) supply their own.
- FleetPy scenario files are generated from one template per area instead of one file per fleet size.
- FleetPy inputs are staged from the area's folder, not from a fixed list.
- I-05: a run never overwrites a frozen input.
- Item 7 (downtown node file) changes results: done when decision 6 says.

### Phase 4: input checker

`tools/check_study_area.py <area>`, also called by the run at startup, stops with a clear message before any work if:

- a required file or column is missing;
- the node-numbering rule is broken;
- a trip end is not a walk node, or an FRT stop is not joined to a walk node;
- the node -> zone mapping misses nodes;
- FleetPy's road nodes do not match the walk nodes;
- a super-network has two links with the same `(from_node, to_node)` (I-34, item 3);
- the walk network is not connected.

### Phase 5: building the networks from basic inputs

(Only if decision 1 is (a) or (c).)

- A user supplies basic inputs: road nodes and edges (with the link kind of I-33), FRT stops, links and routes,
  demand, zone data.
- One command builds everything the run reads, with `pre_process/build_super_network.py` (the I-33 version from
  `TRA_input_data_prep`): every headway x virtual-stop-share variant, `auto_edges`, the FleetPy network folder, and
  (decision 8) one set per time period.
- The demand format (one row per traveler with that traveler's `bt_*` coefficients, `income`, `transit_pass`,
  `parking_dur_min`, ...) is documented. `pre_process/generate_demand_files.py` stays as the SANDAG/ActivitySim
  example of how to produce it.

### Phase 6: prove it with a second area

- A small synthetic test area (a few dozen nodes, two FRT routes, about 100 travelers; a run of a minute or less),
  shipped in the repository as a quick check that a non-Lemon-Grove area runs end to end (decision 7).
- Then downtown San Diego (I-34) as the real second area.

### Phase 7: documentation

README section "Add your own study area": what to supply (link to `docs/study_area_inputs.md`), how to build and check
it, how to run it, and where the outputs are. Lemon Grove is the worked example.

## Decisions needed from the user

1. **Input level.** What does a user supply?
   - (a) Basic inputs; the builder makes the super-networks (recommended: users do not have to reproduce the
     super-network format by hand, and I-33/I-35 already rely on the builder).
   - (b) Finished super-networks.
   - (c) Both.
2. **Where the area-specific values live.**
   - (a) One full parameter file per area in `mtsm_data/<area>/` (recommended: fares, costs and node counts differ by
     area too; the existing `--config` option already takes a file).
   - (b) One shared model parameter file plus a small area file.
3. **Node counts** (`num_walk_nodes`, `microtransit_node_offset`).
   - (a) Derived from the network files (recommended: one fewer thing a user can get wrong).
   - (b) Kept as parameters and checked against the files.
4. **File names.**
   - (a) Generic names inside the area folder; the names FleetPy writes into its outputs keep their current form, so
     the reference stays byte-identical (recommended).
   - (b) A full rename, with a documented reference update.
5. **Zone data.**
   - (a) A generic "zone" format (employment, population, income per zone; node -> zone mapping; neighbors for zones
     with no node), with SANDAG's MGRA files as the example (recommended).
   - (b) Keep the SANDAG/MGRA format as the requirement.
6. **Item 7, downtown `pre_nodes.csv` used for the Lemon Grove accessibility.** In every case it is recorded as I-37.
   - (a) Fix now, as its own documented reference update (changes the accessibility values).
   - (b) Fix with the batched new reference.
7. **Test area.**
   - (a) A small synthetic test area (recommended).
   - (b) Downtown San Diego only.
   - (c) Both.
8. **Time periods (I-35).**
   - (a) Define the inputs per time period in Phase 0 now (recommended: the input format is not changed twice).
   - (b) Later.

## Decisions (user, 2026-11-24)

1. **(b) Users supply finished super-networks.** Phase 0 specifies the super-network files (and the other inputs the
   run reads) as they are now. Phase 5 (building the networks from basic inputs) is dropped;
   `pre_process/build_super_network.py` stays as an optional tool that shows how the Lemon Grove networks were made.
2. **(b) One shared model parameter file plus a small area file.** The area file holds what belongs to the study area;
   which parameters go where is settled in Phase 0.
3. **(a) Node counts are derived from the network files** (`num_walk_nodes`, `microtransit_node_offset` leave the
   parameter file).
4. **(a) Generic file names inside the area folder**; the names FleetPy writes into its outputs keep their form, so the
   reference stays byte-identical.
5. **No zone data.** The user does not use the accessibility calculation any more and removes it (step A below).
   Land use, MGRA population/income, MGRA adjacency and the node -> MGRA mapping were read only by it, so a study
   area needs no zone data and decision 5 falls away. (The demand file's `transit_15min_acc` column is a traveler
   attribute passed through to the individual results, not this calculation; it stays.)
6. **Falls away with step A.** The downtown `region/pre_nodes.csv` was read only by the accessibility calculation. The
   finding is recorded as I-37 and closed by the removal. The `wghted_acc_emp_*` values of earlier runs, including
   the reference before 2026-11-24, were computed on the wrong node set.
7. **(a) A small synthetic test area.**
8. **(b) Later.** One network for the whole day for now, as today; the period networks are designed later (I-35 stays
   open).

The plan file itself: saved as this file (user: OK).

### Step A: remove the accessibility calculation (before Phase 0)

User's decisions: delete the six inputs it alone read (they stay in git history); tag the last commit with it as
`last-with-accessibility` (local); drop the three `wghted_acc_emp_*` lines from the evaluation file; do it before
Phase 0. What it changes: `output_performance_metrics.py` (the accessibility functions), `scenarios.py`, `results.py`,
`update_initial_network.py` (no copies into `initial_network_0719/`), three parameters, `mtsm_paths.py`, the
optimizer's `METRIC_COLS`, `tools/check_inputs.py`, `tools/compare_reference.py`, and a reference update (the
evaluation file without the three lines; the four `acc_super_network` files and `intermediate/initial_network_0719/`
leave the reference). Record: `docs/progress.md`, "Accessibility calculation removed".

Effect on the plan: items 6 (zone data) and 7 (downtown node file) are gone, item 1 loses the region and MGRA paths,
item 5 loses I-06; Phase 3 loses its I-06 and item 7 bullets.

### Phase 0: draft written (2026-11-24)

`docs/study_area_inputs.md`: the files, node numbering, link types, columns and units, consistency rules, and seven
open decisions (A-G). All seven decided the same day; G done the same day (node file optional with `whole_region`).

### Phase 1: steps and decisions (user, 2026-11-24)

Steps, one commit each, each ending with a full run that prints `REPRODUCED`:

1. Per-area paths: `mtsm_paths.area_paths(area)` replaces the `LG_*` constants everywhere (model code, tools,
   startup folder creation, the optimizer's output folder). No file moves.
2. Lemon Grove's inputs move to the target layout of `docs/study_area_inputs.md` (`git mv`); `.gitignore`,
   manifest, reference README.
3. Area parameter file `mtsm_data/lemon_grove/area_parameters.csv` (decision A's parameters); the loader reads the
   model file and the area file and stops on a key in both or in neither.

Decisions:

1. The study area's name stays in the model file, renamed `test_area` -> `study_area`; it selects `mtsm_data/<area>/`
   (amends decision A: the area file does not repeat the name).
2. Where the run writes its generated networks: (a), decided after looking at the files. The inputs move to
   `networks/` (the two `base_*` templates become `super_network_micro_virstop_75.csv` and `super_network_frt.csv`,
   the base-headway network `super_network_frt_base_headway.csv`); `initial_network/` keeps only what the run writes.
   A run at the base headway then no longer overwrites an input (I-05).
3. One manifest per area (`mtsm_data/<area>/MANIFEST.csv`), optional for a new area (the startup check uses it when it
   exists); the shared model file stays in `mtsm_data/MANIFEST.csv`.
4. Leftover parts of output file names stay for now: I-40.
5. The three steps above, in that order, one commit each.

Step 1 done 2026-11-24 (`docs/progress.md`, "Phase 1 step 1: per-area paths").
Step 2 done 2026-11-24 (`docs/progress.md`, "Phase 1 step 2: Lemon Grove's inputs in the target layout"); I-05 closed.
Step 3 done 2026-11-24 (`docs/progress.md`, "Phase 1 step 3: area parameter file"). Phase 1 complete.

### Phase 2: steps and decisions (user, 2026-11-24)

Steps, one commit each, each ending with a full run that prints `REPRODUCED`:

1. Remove the Lemon Grove logic: the `if study_area == "lemon_grove"` wrappers (FRT fare and microtransit start
   fare, type-5 update, FRT line duration, the ridership file's `travel_time`), `<area>_vehtype` in
   `create_config_files`, `.gitignore` patterns for any area; and decisions 2 and 3.
2. Derive the node counts from the files (decision 3 of 2026-11-24): `N` = rows of FleetPy's `nodes.csv`, `M` = the
   smallest node of the type-4 links of the microtransit super-network; stop if the files break the numbering rule.
   `num_walk_nodes` and `microtransit_node_offset` leave the area file; and decision 1.

Decisions:

1. I-13: (a) the `micro_only` branch uses the area's last walk node (N - 1); `micro_only_max_walk_node` leaves the
   area file.
2. FleetPy's example check of 88 users: (a) removed.
3. The startup check "only lemon_grove": (a) removed in step 1.
4. The two steps above, one commit each.

Step 1 done 2026-11-24 (`docs/progress.md`, "Phase 2 step 1: no Lemon Grove logic branches").
Step 2 done 2026-11-24 (`docs/progress.md`, "Phase 2 step 2: node numbering derived from the files"); I-13 closed.
Phase 2 complete.

### Phase 3: steps and decisions (user, 2026-11-24)

1. FRT route table: follow the format of `TRA_input_data_prep` (user: "check TRA_input_data_prep for this"). Its
   `build_frt_network.py` writes `frt_routes.csv`, one row per route variant (route x direction) with `route`,
   `direction`, `route_variant`, `n_stops`, `n_links`, `length_m` (inside the area), headways, fare, ... How MTSM's
   line cost uses the rows: decided below, (b2).
2. FleetPy scenario files: (a) generated at run time into FleetPy's staging folder; the tracked per-fleet-size
   files deleted (26: 16 example, 10 debug; "23" in the proposal was a miscount); `forecast_f` written empty (as the tracked 2-vehicle file; a lone space,
   written until now and in 5 tracked files, is read by FleetPy as None too, so no result changed).
3. FleetPy's operator settings stay in `create_config_files`: I-41.
4. The 8 unused files in Lemon Grove's FleetPy network folder deleted (`base.zip`, the two `*_all_infos.geojson`,
   `edges_old.csv`, `sd_edges.csv`, `sd_nodes.csv`, `pre_network/0719_*.csv`).
5. Steps: 1. the route table; 2. the scenario-file generator and the cleanup of 2 and 4. One commit each.

Found for decision 1 (2026-11-24): MTSM's cost takes one one-way length and stop count per route and doubles it
(both directions). Summing the two directions' rows instead gives Lemon Grove's FRT cost and VMT with other
last-digit rounding (tested: equal at some headways, not at others), so a per-direction formula changes the
reference's reported values in their last digits.

Decision 1, final (user, 2026-11-24): (b2), the option that matches `TRA_input_data_prep`: MTSM reads TRA's format
(`route`, `direction`, `n_stops`, `length_m`) and adds up the rows (runs x duration per direction); Lemon Grove's
table has two equal rows per route with half of the route's link distances (the old rule lost a link on routes 856
and 916); a documented reference update.

Step 1 done 2026-11-24 (`docs/progress.md`, "Phase 3 step 1: FRT route table").
Step 2 done 2026-11-24 (`docs/progress.md`, "Phase 3 step 2: FleetPy scenario file written by the run"). Phase 3
complete.
