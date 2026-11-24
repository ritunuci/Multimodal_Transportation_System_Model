# Study-area inputs: what a study area must supply

Status: **final** (2026-11-24, Phase 7 of `docs/study_area_plan.md`): the inputs the code reads after Phases 1-4.
How this file came about (the Phase 0 draft, the Lemon Grove file names until 2026-11-24, decisions A-G) is in
"History" at the end.

This file is the contract between a user and the model: the files a study area supplies, their columns and units, and
the rules that tie them together. It follows the user's decisions of 2026-11-24 (`docs/study_area_plan.md`): the user
supplies **finished super-networks** (decision 1), the node counts are **derived from the files** (decision 3), the
files have **generic names inside the area folder** (decision 4), and there is **one network for the whole day**
(decision 8; per-period networks come with I-35).

Lemon Grove is the worked example throughout.

## The files

A study area is one folder, `mtsm_data/<area>/`. `<area>` is the study area's name, e.g. `lemon_grove`.

| # | File in `mtsm_data/<area>/` | Required |
|---|---|---|
| 1 | `area_parameters.csv` | yes |
| 2 | `demand/demand.csv` | yes |
| 3 | `networks/super_network_micro_virstop_<v>.csv` | yes |
| 4 | `networks/super_network_frt.csv` | yes |
| 5 | `networks/car_network.csv` | yes |
| 6 | `networks/frt_links.csv` | yes (decision B) |
| 7 | `networks/nodes.csv` | only with `aggregation = census_track` (decision G) |
| 8 | `fleetpy/...` (FleetPy's own folder layout) | yes |
| 9 | `networks/super_network_frt_base_headway.csv` | yes (decision C) |
| 10 | `networks/frt_routes.csv` | yes (Phase 3) |

Shared by all study areas: the model parameter file `mtsm_data/input_parameter/mtsm_constant_configurations.csv`
(decision 2: one shared model file plus the small area file 1; the split is decision A).

Optional: `MANIFEST.csv` in the area folder, the checksums of the area's inputs (`python tools/check_inputs.py --write
<area>`). When it exists, a run warns if an input has changed since. Lemon Grove has one (16 files).

Each file is a comma-separated text file with a header row. Column names must be exactly as given.

## Node numbering

Every network file uses one set of integer node numbers. The code relies on this layout:

| Nodes | Numbers | Lemon Grove |
|---|---|---|
| walk nodes = road nodes | `0` to `N - 1` | 0-1098 (N = 1,099) |
| FRT stop nodes | `N` to `M - 1` | 1099-1170 (71 of them are used) |
| microtransit nodes | `M` to `M + N - 1` | 1171-2269 (M = 1,171) |

- Walk node `i` is the road node `i`, FleetPy's node `i` (`node_index` in FleetPy's `nodes.csv`), and the
  microtransit node `M + i`.
- `N` (`num_walk_nodes`) and `M` (`microtransit_node_offset`) are derived from the files (decision 3): `N` = the
  number of rows of FleetPy's `nodes.csv`; `M` = the smallest node of the microtransit in-vehicle links (type 4).
  Since 2026-11-24 (Phase 2 step 2, `config.derive_node_numbering`); until then they were parameters. The run stops
  with a message if FleetPy's `node_index` is not 0..N-1, if the type-4 nodes are not M..M+N-1 (the same in every
  virtual-stop share's file), or if a type-5 link does not join walk node i and microtransit node M + i.
- Every trip starts and ends at a walk node. The car network uses the walk node numbers.

## Link types

All network files (3, 4, 5, 6, 9) have the columns `from_node, to_node, distance, travel_time, link_type, route` (file 6
writes `distance (meters)` instead of `distance`).

- `distance`: meters. `travel_time`: seconds. `route`: an integer; `-1` where there is no route.
- One row per direction: a two-way road is two rows.
- Any `link_type` other than the ones below stops the run.

| Type | Meaning | From -> to | `distance` | `travel_time` | `route` | In file |
|---|---|---|---|---|---|---|
| 0 | walk | walk node -> walk node, one per road edge and direction | road length | length / walk speed (Lemon Grove: 1.251 m/s) | -1 | 3, 4 |
| 1 | FRT in-vehicle | stop node -> next stop node of the same route | line length between the stops | FRT run time | route number | 3, 4, 6 |
| 2 | FRT boarding | walk node -> stop node | 0 | > 0 (half the headway; see below) | -1 | 3, 4 |
| 2 | FRT alighting | stop node -> walk node | 0 | 0 | -1 | 3, 4 |
| 4 | microtransit in-vehicle | microtransit node -> microtransit node, one per road edge and direction | road length | car time x factor (Lemon Grove: 1.4) | -1 | 3 |
| 5 | microtransit boarding | walk node `i` -> microtransit node `M + i`, only at virtual stops | 0 | initial wait (Lemon Grove: 180) | -1 | 3 |
| 5 | microtransit alighting | microtransit node `M + i` -> walk node `i`, only at virtual stops | 0 | 0 | -1 | 3 |
| 7 | car | road node -> road node, one per road edge and direction | road length | car time | -1 | 5 |

What the run does with them:

- **Type 2:** for each scenario headway the run sets every type-2 link with `travel_time` other than 0 to
  `headway x 60 / 2` and writes the result as `initial_super_network_..._hw_<headway>...` (so the headway the supplied
  file was built with does not matter). The FRT fare is charged on a type-2 link from a walk node to a stop node, so a
  boarding link must have a travel time above 0 and an alighting link exactly 0.
- **Type 4:** in each iteration, times are multiplied by FleetPy's detour ratio of the period. The distance fare of
  microtransit is charged per meter of `distance`.
- **Type 5:** in each iteration, the boarding times are replaced by FleetPy's average waiting time of the period. The
  microtransit start fare and the rejection penalty are charged here.
- **Virtual stops** are the walk nodes that have type-5 links. Lemon Grove's file has 815 of the 1,099 walk nodes. The
  `<v>` in the file name is the share in percent and must equal the parameter `virtual_stop_scenarios`; the run does
  not count the stops.
- **One link per node pair.** The networks are read into a `networkx.DiGraph`, which keeps only the last link of a
  `(from_node, to_node)` pair. Lemon Grove's road network has 8 parallel pairs (two different roads between the same
  two nodes), so 8 of its walk, car and microtransit links are dropped. FleetPy also keeps the last edge of a pair.
  The checker lists such pairs as a warning; the run goes on (decision E).

## 1. Area parameter file (`area_parameters.csv`)

Same format as the model parameter file: `parameter_name,parameter_value,description`. Content (decision A,
including the local prices and costs). In use since 2026-11-24 (Phase 1 step 3): `config.read_constant_config` reads
the model file and this file and stops if a key is in the wrong file, missing or repeated
(`mtsm_global_parameters.AREA_PARAMETERS` lists this file's keys).

| Parameter | Lemon Grove | In the model file until 2026-11-24 as |
|---|---|---|
| `virtual_stop_scenarios` | 75 | same (must match file 3's name) |
| `base_frt_headway` (min) | 20 | same |
| `base_frt_fare` ($) | 2.5 | same |
| `frt_operating_hours` | 19 | same |
| `frt_speed_mph` | 30 | same |
| `frt_dwell_time_min` | 3 | same |
| `frt_dead_end_time_min` | 20 | same |
| `frt_operating_cost_per_veh_hour` ($) | 170 | same |
| `micro_operating_cost_per_veh_hour` ($) | 130 | same |
| `f_gas_per_mile` ($/mile, FRT fuel) | 0.35 | same |
| `m_gas_per_mile` ($/mile, microtransit fuel) | 0.55 | same |
| `car_gas_cost_per_meter` ($/m) | 0.00025 | same |
| `parking_rate_peak`, `parking_rate_offpeak` ($ per interval) | 1, 0.5 | same |
| `parking_charge_interval_min` | 30 | same |

The study area's name is not in this file: it is `study_area` in the model file (`test_area` until 2026-11-24;
Phase 1 decision 1), which selects `mtsm_data/<area>/`.

Removed from the parameter files on 2026-11-24 (Phase 2 step 2; they were in this file from Phase 1 step 3 until
then): `num_walk_nodes`, `microtransit_node_offset` (derived from the files, decision 3) and
`micro_only_max_walk_node` (the `micro_only` branch uses the area's last walk node, I-13). Lemon Grove's file has
15 parameters.

## 2. Demand (`demand/demand.csv`)

One row per traveler (Lemon Grove: 3,742). The rows need not be sorted.

| Column | Type | Meaning |
|---|---|---|
| `rq_time` | integer | departure time, seconds after midnight (Lemon Grove: 18,157-86,276) |
| `start`, `end` | integer | origin and destination walk node |
| `request_id` | integer | the traveler's id; unique |
| `bt_c_0` | number | car constant (Lemon Grove: 0 for all) |
| `bt_c_ivt` | number | car in-vehicle time, per minute |
| `bt_c_gas` | number | car out-of-pocket cost (fuel and parking), per $ |
| `bt_t_0` | number | transit constant |
| `bt_t_wk` | number | walking time, per minute |
| `bt_f_wt`, `bt_m_wt` | number | FRT / microtransit waiting time, per minute |
| `bt_f_ivt`, `bt_m_ivt` | number | FRT / microtransit in-vehicle time, per minute |
| `bt_f_trfer` | number | per transfer (used only when `enable_num_transfer_penalty` is on) |
| `bt_t_fr` | number | transit fare and rejection penalty, per $; the logsum is divided by it |
| `income` | integer | reported in the individual results only |
| `transit_15min_acc` | number, optional | reported in the individual results only |
| `transit_pass` | integer, optional | not used |
| `parking_dur_min` | number, optional | parking duration (min); missing = 0 (no parking cost) |

- The coefficients are positive: the generalized cost is a disutility (a choice probability is `exp(-cost)` over the
  sum), and a negative link cost stops the run.
- Each traveler has their own coefficients. `pre_process/generate_demand_files.py` is the SANDAG/ActivitySim
  example of how Lemon Grove's file was made.

## 3. Super-network with microtransit (`networks/super_network_micro_virstop_<v>.csv`)

Link types 0, 1, 2, 4, 5 (see "Link types"). Lemon Grove: 7,534 links (2,816 walk, 130 FRT, 142 FRT boarding and
alighting, 2,816 microtransit in-vehicle, 1,630 microtransit boarding and alighting).

## 4. FRT-only super-network (`networks/super_network_frt.csv`)

Link types 0, 1, 2: the walk and FRT links of file 3, without microtransit. Used for the base case and for the
scenario's travelers outside the microtransit operating periods, in both cases at `base_frt_headway`, not at the
scenario's `frt_headway` (`paths.networks_for_traveler`; so in the original code too; I-38). Lemon Grove: 3,088
links.

The base case runs on this network at `base_frt_headway`, supplied as file 9 (decision C: it stays an input). File 9
is file 4 with every FRT boarding time (type 2, `travel_time` above 0) set to `base_frt_headway x 60 / 2`. Checked
2026-11-24: rebuilding it from file 4 that way gives Lemon Grove's file byte for byte. A run with `frt_headway`
equal to the base headway overwrote it until 2026-11-24 (I-05; since Phase 1 step 2 the run reads file 9 from
`networks/` and writes its own networks into `initial_network/`).

## 5. Car network (`networks/car_network.csv`)

Link type 7 only, between walk node numbers. Lemon Grove: 2,816 links, row for row FleetPy's road edges (same
`distance` and `travel_time`).

## 6. FRT links (`networks/frt_links.csv`)

The FRT in-vehicle links (type 1), with the column `distance (meters)`. Used as the rows of the FRT ridership output
files (until 2026-11-24 also for the FRT line length, number of stops and line duration, now from file 10). Lemon
Grove: 130 links, the type-1 links of files 3 and 4 in the same order (the distances differ from the super-network's
in the 7th decimal place).

- Until 2026-11-24 the line length of a route was the sum of its links' *distinct* distances. This halved the length
  only because the old network has the same distance in both directions (I-34, item 1), and it lost links of equal
  length (Lemon Grove routes 856 and 916). Replaced by the route table, file 10.

## 10. FRT route table (`networks/frt_routes.csv`)

One row per route variant, i.e. route and direction: the format of `frt_routes.csv` written by
`build_frt_network.py` in `TRA_input_data_prep` (Phase 3 decision 1, 2026-11-24). The run reads four columns; any other
columns (TRA writes `route_variant`, mode, operator, the ABM3 headways, fare, ...) are ignored.

| Column | Type | Meaning |
|---|---|---|
| `route` | integer | the route number, as in file 6 |
| `direction` | integer | the direction (ABM3: 1, 2) |
| `n_stops` | integer | stops of this route and direction (at least 2) |
| `length_m` | number | length of this route and direction inside the area (m), the sum of its links' distances |

- Each row is one direction: per day it runs `frt_operating_hours x 60 / headway` times, each run taking
  `length / frt_speed_mph + n_stops x frt_dwell_time_min + frt_dead_end_time_min`. The FRT operating cost, fuel cost
  and vehicle miles add up the rows (until 2026-11-24: one row per route, doubled for the two directions).
- A route of file 6 without a row, a row for a route that has no link, a repeated route and direction, `length_m`
  <= 0 or `n_stops` < 2 stop the run.
- Lemon Grove: 12 rows, routes 4, 856, 916, 917, 936, 520 in directions 1 and 2. Its FRT network has the same links
  in both directions, so each direction gets half of the route's link distances in file 6 (unrounded) and the
  route's stop nodes; the two rows of a route are equal.

## 7. Node file (`networks/nodes.csv`)

Optional (decision G). Read only when the model parameter `aggregation` is `census_track` (FleetPy's waiting times
averaged per zone). With `whole_region` (the setting in use) the run puts every walk node in one zone and does not
read the file: every zone gets the same period average there, so the zones would not matter
(`get_microtransit_skims.get_node_ct`, since 2026-11-24).

When it is needed, one row per walk node:

| Column | Meaning |
|---|---|
| `node_in_fleetpy` | walk node number (0 to N - 1) |
| `census_tract` | integer zone of the node |

Other columns may be present and are ignored. Lemon Grove's file has seven (`node_index` = SANDAG node id,
`is_stop_only`, `pos_x`, `pos_y`, `is_demand_node` as well), with 23 census tracts; it stays in the repository.

## 8. FleetPy inputs (`fleetpy/`)

In FleetPy's own folder layout; the run copies them into `fleetpy/` before each FleetPy run. Names that FleetPy writes
into its outputs keep the area prefix (decision 4).

| File | Content |
|---|---|
| `data/networks/<area>_example_network/base/nodes.csv` | `node_index` (0 to N - 1), `is_stop_only`, `pos_x`, `pos_y` |
| `data/networks/<area>_example_network/base/edges.csv` | `from_node, to_node, distance` (m), `travel_time` (s), `source_edge_id` |
| `data/networks/<area>_example_network/base/crs.info` | coordinate system of `pos_x, pos_y`, e.g. `EPSG:2230` (Lemon Grove's is wrong: I-39) |
| `data/fleetctrl/initial_vehicle_distribution/<area>_example_network/imbalanced.csv` | `node_index, probability`: where vehicles start; probabilities sum to 1 (Lemon Grove: 5 nodes, 0.2 each; I-36) |
| `data/vehicles/<area>_vehtype.csv` | FleetPy vehicle type (Lemon Grove: capacity 8) |
| `studies/example_study/scenarios/<area>_constant_config_ir_repo.csv` | FleetPy constant config with repositioning; `network_name` = `<area>_example_network`, `demand_name` = `<area>_example_demand` |
| `studies/example_study/scenarios/<area>_constant_config_ir.csv` | the same without repositioning (`repositioning_list` False) |

FleetPy's scenario file (`<area>_example_ir_heuristics_repositioning_<fleet>_veh.csv`, or `..._ir_only_...`) is not an
input: since 2026-11-24 the run writes it for its fleet size into FleetPy's own scenarios folder
(`fleetpy_runner.scenario_config_file`; the operator settings in it are fixed in the code, I-41). Until then one
tracked file per fleet size was kept here.

- FleetPy's road edges are the road edges of files 3 and 5: same node pairs, distances and car times, in the same
  order (checked for Lemon Grove).
- FleetPy reads `crs.info` on startup and uses it only to convert coordinates to latitude/longitude; the run's results
  do not depend on it.

## Consistency rules

Checked since 2026-11-24 by `tools/check_study_area.py` (Phase 4), which every run calls at startup and which also runs
on its own (`python tools/check_study_area.py [area]`). A broken rule is an error that stops the run before any work,
except where it says "warning". Lemon Grove: no error, one warning (rule 9), in about 1.5 s.

1. Every file above exists with its columns; every value has the right type.
2. Node numbering: FleetPy's nodes are `0..N-1`; walk, car and type-0 links use only walk nodes; type-1 links only
   stop nodes; type-4 links only microtransit nodes; type-5 links join `i` and `M + i`.
3. Type 2: boarding (walk -> stop) has `travel_time` > 0, alighting (stop -> walk) has 0.
4. Every trip's `start` and `end` is a walk node; `request_id` is unique; no travel coefficient (`bt_*`) is negative.
   A trip departing at or after FleetPy's `end_time` (its constant config) is a warning (decision 3; I-35).
5. FleetPy's edges, the walk links (type 0) and the microtransit links (type 4, minus M) are the same road edges
   (node pairs and distances); the car network has all of them and may have more (I-33: freeways for cars only).
6. Files 3, 4, 6 and 9 have the same FRT links; file 9 is file 4 at `base_frt_headway`. File 10 has the routes of
   file 6 (checked by the run).
7. With `aggregation = census_track`: the node file exists and `node_in_fleetpy` covers every walk node.
   `aggregation` is `whole_region` or `census_track`.
8. `<v>` in file 3's name equals `virtual_stop_scenarios`.
9. No two links with the same `(from_node, to_node)`; a warning that names them, not an error (decision E). The road
   network's own duplicates are reported once (Lemon Grove: 8 pairs), not again for each network file.
10. Every trip's origin can reach its destination on foot and FRT (file 4), and by car (file 5). Not checked: whether a
   network is one strongly connected part (Phase 4 decision 4: `TRA_input_data_prep` builds its networks that way, and
   this trip-level rule is what the model needs; Lemon Grove's current road network has 4 isolated islands of 11
   nodes with no trip and no FRT stop).
11. FleetPy: `nodes.csv`, `edges.csv`, `crs.info`, `imbalanced.csv` and the vehicle type exist; the vehicle start
   nodes are walk nodes and their probabilities sum to 1; each constant config of the run (`repositioning_list`) names
   `<area>_example_network` and `<area>_example_demand`, and `imbalanced.csv` as the start distribution.

## What the run writes (not inputs)

In `mtsm_data/<area>/`: the scenario networks (`initial_super_network_micro_hw_<h>_virstop_<v>.csv`,
`initial_super_network_non_micro_hw_<h>.csv`), the final networks per period (`final_network/`), FleetPy's user
statistics per iteration (`indiv_output/`), and the results (`output/`: the evaluation file, the individual results
and the FRT ridership files); in `fleetpy/`: the demand handed to FleetPy and FleetPy's results.

## Not supported for a new study area (for now)

- `micro_only` (microtransit without FRT): it needs a network `initial_super_network_micro_only_virstop_<v>.csv`
  that no study area has (I-13).
- Networks per time period (I-35).

## History

Moved here unchanged on 2026-11-24 (Phase 7, decision 7), when the file was marked final.

- Status line until then: Status: **draft** (Phase 0 of `docs/study_area_plan.md`; written 2026-11-24 against the code
  after step A, the accessibility removal). Decisions A-G made 2026-11-24 (section "Decisions (user, 2026-11-24)" at
  the end).
- Until then the introduction said: The names below are the **target names** (after Phases 1-3 of the plan). Since
  2026-11-24 (Phase 1 step 2) Lemon Grove's inputs have them, except the area file (step 3); the table "The files"
  also gives the names they had until then. Lemon Grove is the worked example throughout.
- The manifest count above said 40 files until 2026-11-24; Lemon Grove's manifest has 16.

### The files, with the Lemon Grove names until 2026-11-24

| # | Target file in `mtsm_data/<area>/` | Lemon Grove file until 2026-11-24 | Required |
|---|---|---|---|
| 1 | `area_parameters.csv` | (part of `input_parameter/mtsm_constant_configurations.csv`) | yes |
| 2 | `demand/demand.csv` | `demand_data/lemon_grove_trips_nodes_study_area_with_beta.csv` | yes |
| 3 | `networks/super_network_micro_virstop_<v>.csv` | `initial_network/base_super_network_lemon_grove_micro_hw_10_virstop_75.csv` | yes |
| 4 | `networks/super_network_frt.csv` | `initial_network/base_super_network_lemon_grove_non_micro_hw_10.csv` | yes |
| 5 | `networks/car_network.csv` | `initial_network/auto_edges.csv` | yes |
| 6 | `networks/frt_links.csv` | `transit/super_network_transit_edges.csv` | yes (decision B) |
| 7 | `networks/nodes.csv` | `transit/network_folder/pre_nodes.csv` | only with `aggregation = census_track` (decision G) |
| 8 | `fleetpy/...` (FleetPy's own folder layout) | `fleetpy_inputs/...` | yes |
| 9 | `networks/super_network_frt_base_headway.csv` | `initial_network/initial_super_network_non_micro_hw_20.csv` | yes (decision C) |
| 10 | `networks/frt_routes.csv` | (new 2026-11-24; the line lengths were computed from file 6) | yes (Phase 3) |

### Lemon Grove values in the code (not inputs; removed in Phases 1-3)

- `microtransit.py`: FleetPy's result check `{"number users": 88}`.
- `fleetpy_runner.create_config_files`: the vehicle type name `lemon_grove_vehtype`.
- The `if study_area == "lemon_grove"` branches and `LG_*` paths (`docs/study_area_plan.md`, items 1-2).
- 2026-11-24: all three removed (paths in Phase 1 step 1; the branches, the vehicle type name and the check of 88
  users in Phase 2 step 1).

### Decisions needed

- **A. Parameter split** (decision 2). Proposed above for the area file: the study area's name, its virtual-stop
  share, its base FRT service (headway, fare) and its FRT line data (operating hours, speed, dwell, dead-end time).
  Open: the local prices and costs. Do these go to the area file too (recommended: they differ between regions) or
  stay in the model file?
  - `frt_operating_cost_per_veh_hour`, `micro_operating_cost_per_veh_hour`
  - `f_gas_per_mile`, `m_gas_per_mile`, `car_gas_cost_per_meter`
  - `parking_rate_peak`, `parking_rate_offpeak`, `parking_charge_interval_min`

  Everything else stays in the model file: the fares, fleet size and headway the optimizer varies, the fare factors,
  the rejection values, the seed, the iteration and convergence settings, the time periods and the scenario lists.
- **B. FRT links file (6).**
  - (a) Keep it as an input for now (recommended: deriving it from the type-1 links changes the printed distances in
    the 7th decimal place, and so the reference; the route table of I-34 replaces it later).
  - (b) Derive it from file 3 now, with a documented reference update.
- **C. Base-headway FRT network.**
  - (a) The run derives it from file 4 at `base_frt_headway` (recommended: byte-identical for Lemon Grove, one input
    fewer, and it ends the overwrite of a frozen file, I-05).
  - (b) Keep it as an input.
- **D. Target names and layout:** the names in "The files" (`area_parameters.csv`, `demand/demand.csv`,
  `networks/...`, `fleetpy/...`). Agree, or name changes.
- **E. Duplicate node pairs** (8 parallel road pairs in Lemon Grove).
  - (a) The checker warns and names them; the run keeps the last link, as today (recommended: Lemon Grove keeps
    reproducing).
  - (b) The checker stops the run; Lemon Grove's networks are fixed first (changes results: new reference).
- **F. Lemon Grove's `crs.info`** says `EPSG:32632` (UTM zone 32N, in Germany), but the coordinates look like
  California State Plane zone 6 in US feet (`EPSG:2230`), likely a leftover of FleetPy's example data (like I-10).
  - (a) Correct it to the right code after checking (recommended; it should not change any result, which a full run
    will confirm).
  - (b) Leave it and document it.
- **G. Node file (7).**
  - (a) Require only `node_in_fleetpy` and `census_tract` (recommended; the other columns may be there).
  - (b) Keep requiring all of Lemon Grove's columns.

### Decisions (user, 2026-11-24)

- **A:** yes; the local prices and costs go to the area file too (section 1).
- **B:** (a) keep the FRT links file (6) as an input.
- **C:** (b) keep the base-headway FRT network as an input (file 9, `networks/super_network_frt_base_headway.csv`);
  I-05 stays open (closed the same day by Phase 1 step 2, which separates the run's networks from the inputs).
- **D:** agreed.
- **E:** (a), after a fuller explanation: the checker warns about duplicate node pairs and names them; the run keeps
  the last link, as today. (Lemon Grove: 3 parallel road pairs, both directions, plus 2 loops listed twice; in each
  pair the kept edge is the slower one; FleetPy also keeps the last.)
- **F:** the run does not need the file; leave it for now and fix it later: I-39.
- **G:** replaced by (c) after checking that `census_tract` does not matter with `whole_region`: the node file is
  optional and read only with `aggregation = census_track`. Done the same day (`get_node_ct`; full run
  `REPRODUCED`; `docs/progress.md`, "Node file optional with whole_region").
- Also recorded on the user's request: I-38 (outside the microtransit operating periods, scenario travelers ride the
  FRT at the base headway).
