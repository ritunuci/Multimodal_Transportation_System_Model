# Moving TRA's new Lemon Grove inputs into `mtsm_data/lemon_grove/` (2026-11-26)

Branch `TRA_resubmission` only; `main` keeps the old Lemon Grove inputs and their reference
(`docs/reference_results/lemon_grove_seed0`). This file records which file of the new data went where, under which
name, which old inputs were deleted or kept, and how `networks/frt_links.csv` was written.

## Source and decisions

- **Source:** `new_LG_data/lemon_grove/` (untracked; put there by the user on 2026-11-24), written by the
  input-preparation repository `TRA_input_data_prep` (https://github.com/ritunuci/TRA_input_data_prep): SANDAG ABM3,
  MGRA15 zones, the freeway build (freeways, connectors and ramps car only, I-33), one super-network per ABM3 period
  (I-35). The `TRA_input_data_prep` commit that built the files is not recorded yet (held decision 7).
- **User's decisions (2026-11-26):** replace the old Lemon Grove inputs in place (so held decision 1 is (a)); the
  lists below as given; empty the four run-output folders; move the files only. The time periods in
  `area_parameters.csv`, FleetPy's `end_time` and the other held decisions (demand size, modes, virtual-stop shares,
  area parameter values) come later.
- **How:** a script in the session scratchpad (not in the repository). Every file is a byte-for-byte copy
  (`shutil.copyfile`), compared with its source afterwards (`filecmp.cmp(..., shallow=False)`: all 25 identical).
  Line endings stay as TRA wrote them (CRLF); the repository stores files byte for byte (`.gitattributes`: `* -text`).
  File numbers are those of `docs/study_area_inputs.md`.

## Copied files (25)

Source paths are relative to `new_LG_data/lemon_grove/`, destinations to `mtsm_data/lemon_grove/`.
`<P>` is each of the five ABM3 periods `EA`, `AM`, `MD`, `PM`, `EV` (one file each).

| # | Source (name before) | Destination (name after) | Renamed | Rows | Note |
|---|---|---|---|---|---|
| 2 | `demand/lemon_grove_trips_nodes_study_area_with_beta.csv` | `demand/demand.csv` | yes | 42,698 | all trips; the size is held decision 2 (old file: 3,742) |
| 3 | `super_network/initial_super_network_micro_hw_10_virstop_75_<P>.csv` | `networks/super_network_micro_virstop_75_<P>.csv` | yes (`initial_` and `_hw_10` dropped) | 7,064 each | 5 files; FRT boarding 300 s (headway 10), as `main`'s file 3; the run sets the scenario headway itself |
| 4 | `super_network/initial_super_network_non_micro_hw_10_AM.csv` | `networks/super_network_frt.csv` | yes | 2,928 | TRA's five period files of a headway are byte-identical, so the AM one stands for all |
| 9 | `super_network/initial_super_network_non_micro_hw_20_AM.csv` | `networks/super_network_frt_base_headway.csv` | yes | 2,928 | `base_frt_headway` 20: FRT boarding 600 s = 20 x 60 / 2, as file 9 requires; another base headway (held decision 6) takes that headway's file |
| 5 | `super_network/auto_edges_<P>.csv` | `networks/car_network_<P>.csv` | yes (`auto_edges` -> `car_network`) | 2,601 each | 5 files; link type 7, every road edge incl. the 27 car-only edges |
| 10 | `frt/frt_routes.csv` | `networks/frt_routes.csv` | no | 12 | 7 routes (4, 520, 851, 856, 916, 917, 936); the run reads `route`, `direction`, `n_stops`, `length_m` and ignores the other columns |
| 8 | `fleetpy_network/base/nodes.csv` | `fleetpy/data/networks/lemon_grove_example_network/base/nodes.csv` | no | 1,067 | |
| 8 | `fleetpy_network/base/edges.csv` | `fleetpy/data/networks/lemon_grove_example_network/base/edges.csv` | no | 2,574 | the walk and microtransit edges (no car-only edges) |
| 8 | `fleetpy_network/base/crs.info` | `fleetpy/data/networks/lemon_grove_example_network/base/crs.info` | no | | `EPSG:2230` (I-39) |
| 8 | `fleetpy_network/network_dynamics.csv` | `fleetpy/data/networks/lemon_grove_example_network/network_dynamics.csv` | no | 6 | new: switches at 0, 10800, 21600, 32400, 55800, 68400 s |
| 8 | `fleetpy_network/<t>/edges_td_att.csv` for `<t>` = 0, 10800, 21600, 32400, 55800, 68400 | `fleetpy/data/networks/lemon_grove_example_network/<t>/edges_td_att.csv` | no | 2,574 each | new: 6 files, FleetPy's travel times from time `<t>` on |
| 8 | `fleetpy_initial_vehicle_distribution/imbalanced.csv` | `fleetpy/data/fleetctrl/initial_vehicle_distribution/lemon_grove_example_network/imbalanced.csv` | no | 5 | nodes 694, 225, 863, 498, 189, 0.2 each (I-36) |

## Written from the new data (1): `networks/frt_links.csv` (file 6)

`TRA_input_data_prep` does not write this file. TRA's `frt/frt_edges.csv` cannot replace it: it numbers the stops
with TRA's stop ids (e.g. 4117885), not with MTSM's node numbers.

How it was written:

1. **Source:** `super_network/initial_super_network_micro_hw_10_virstop_75_AM.csv`, the source of file 3 for AM.
2. **Rows:** every line of that file whose fifth field (`link_type`) is `1`, the FRT in-vehicle links, in the order
   of the file, copied as bytes (the numbers are not read and written again, so no digit changes). 110 links.
3. **Header:** the source's header with one column renamed, `distance` -> `distance (meters)` (the name the run and
   the checker expect, as in `main`'s file):
   `from_node,to_node,distance (meters),travel_time,link_type,route`.
4. **Line endings:** CRLF, as in the source.

The same procedure as a short script (the code that was run, without its checks):

```python
lines = open(src_file_3_AM, "rb").read().splitlines(keepends=True)
header, rows = lines[0], lines[1:]
frt_rows = [r for r in rows if r.strip() and r.split(b",")[4].strip() == b"1"]
eol = header[len(header.rstrip(b"\r\n")):]          # b"\r\n"
out = b"from_node,to_node,distance (meters),travel_time,link_type,route" + eol + b"".join(frt_rows)
open("mtsm_data/lemon_grove/networks/frt_links.csv", "wb").write(out)
```

Checked before writing: the type-1 lines are identical, in the same order, in all five period files of file 3
(`..._virstop_75_EA` ... `_EV`) and in the two FRT-only files (files 4 and 9), so the file fits every network
(consistency rule 6). Checked after: the written file equals these bytes; 111 lines, all CRLF; SHA-256
`14fff4cb36763160ee766ffd5d563589498bce3ef55bb5c9693bbd798c9d0b4c`. The FRT distances are in metres (I-31, checked
2026-11-26 against TRA's mileposts).

## Deleted old inputs (3)

| Old file in `mtsm_data/lemon_grove/` | Why |
|---|---|
| `networks/super_network_micro_virstop_75.csv` | the whole-day file 3; replaced by the five period files (the run and the checker stop if both forms exist) |
| `networks/car_network.csv` | the whole-day file 5; replaced by the five period files (same rule) |
| `networks/nodes.csv` | file 7, optional, read only with `aggregation = census_track`; it describes the old network, and TRA's node file (`network/nodes.csv`) has no `census_tract`, so the new data cannot use `census_track` |

## Replaced old inputs (9)

Same path, new content: `demand/demand.csv`, `networks/super_network_frt.csv`,
`networks/super_network_frt_base_headway.csv`, `networks/frt_routes.csv`, `networks/frt_links.csv` (written as
above), FleetPy's `base/nodes.csv`, `base/edges.csv`, `base/crs.info` and `imbalanced.csv`. The old versions stay
in `main` and in the git history.

## Kept old inputs (4, plus the manifest)

| File in `mtsm_data/lemon_grove/` | To do |
|---|---|
| `area_parameters.csv` | unchanged for now. Before a run it needs the ABM3 periods (`time_periods` `EA;AM;MD;PM;EV`, `period_start_h` 3, `period_end_h` `6;9;15.5;19;27`, `peak_periods` `AM;PM`): with the old four periods there is no period `EA` for the `_EA` files, and the run and the checker stop. The other values: held decision 6 |
| `fleetpy/data/vehicles/lemon_grove_vehtype.csv` | unchanged (capacity 8) |
| `fleetpy/studies/example_study/scenarios/lemon_grove_constant_config_ir.csv`, `..._ir_repo.csv` | unchanged; `end_time` 86400 (24:00) is before the last departures (97,043 s, 26:57; 200 trips after midnight): to be set with the held decisions |
| `MANIFEST.csv` | rewritten (`python tools/check_inputs.py --write lemon_grove`): 30 inputs (16 before); `check_inputs.py` then passed |

## Run outputs removed (not inputs)

The four folders of run outputs held only files of runs on the old data (ignored by git): `final_network/` 100,
`initial_network/` 34, `indiv_output/` 13, `output/` 171 files (318; including names from before I-40 and the
optimizer tests). All removed, the `.gitkeep` of each folder kept. A run on `main` writes them again.

## Not moved (stay in `new_LG_data/lemon_grove/`)

The model does not read them; they are TRA's build records and inputs:

- `demand/lemon_grove_debug_trips_nodes_study_area_with_beta.csv` (TRA's 1 % debug sample, 427 trips; for held
  decision 2), `demand/lemon_grove_dropped_trips.csv`, `demand/lemon_grove_trips_trace.csv`;
- `super_network/`: the other headways (15, 20, 30, 60 for file 3; 15, 30, 60 for the FRT-only files), the
  virtual-stop shares 50 and 100 (held decision 5), the `micro_only` files, the other periods of the FRT-only files
  (identical), `super_network_info.csv` (the builder's settings: walk speed 1.6 m/s, `micro_time_factor` 1.4 (I-35),
  microtransit wait 180 s, virtual-stop seed 42), `inputs/` (the builder's inputs: road edges per period, local edges,
  virtual stops);
- `frt/`: `frt_edges.csv`, `frt_stops.csv` and the shapefiles;
- `network/` (raw and processed road network, edge and node kinds, period link times, shapefiles) and `mapping/`
  (MGRA <-> node).

## Not done yet

- `tools/check_study_area.py` and a run: they need the ABM3 periods in `area_parameters.csv` (held decisions).
- The Lemon Grove numbers in `docs/study_area_inputs.md` and `README.md` (e.g. 3,742 travelers, 7,534 links) still
  describe the old data; to update with the branch's new reference.
- `docs/reference_results/lemon_grove_seed0` is `main`'s reference; `compare_reference.py` reports `NOT REPRODUCED`
  on the branch until the new reference replaces it.
