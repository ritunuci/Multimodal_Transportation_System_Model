# FleetPy: base version and local changes

This folder is [FleetPy](https://github.com/TUM-VT/FleetPy) (MIT license, see `LICENSE`), the fleet simulation that
the Multimodal Transportation System Model (MTSM, the rest of this repository) runs for microtransit. This file lists
everything in this folder that differs from upstream FleetPy, so that FleetPy can be updated or replaced without losing
a change, and so that the model's methods can state exactly which FleetPy it uses.

## Base version

**Upstream commit `7019960`** (`70199600297afd8fbc8dc256586dd064e0277599`, 2022-10-10, branch `main`,
"Broker, Reactive Repositioning, Scenario GUI").

How it was found (2026-11-07): every commit on every branch of `https://github.com/TUM-VT/FleetPy` was compared with
this folder, file by file, ignoring line endings. `7019960` contains 90 of the 97 files in `src/` byte for byte; no
commit contains more. No upstream file in `src/`, `data/` or `studies/` is missing here, and no code file was added.
The 7 other `src/` files differ only by the local changes below. Upstream FleetPy has moved on since (latest commit
2026-10-01); this repository has not been updated to it.

Line endings: files here use CRLF, upstream uses LF. This is not counted as a change.

## How MTSM uses FleetPy

- Only `fleetpy_runner.py` (repository root) imports FleetPy. It puts this folder on `sys.path`, because FleetPy
  imports itself as the top-level package `src`.
- FleetPy finds `data/` and `studies/` next to `src/`, so they stay in this folder.
- MTSM's Lemon Grove inputs for FleetPy are kept in `mtsm_data/lemon_grove/fleetpy_inputs/` (same folder layout as this
  folder) and copied into this folder before each FleetPy run (`fleetpy_runner.stage_inputs`). The copies are
  git-ignored.
- In every iteration, MTSM writes the demand for FleetPy into
  `data/demand/lemon_grove_example_demand/matched/lemon_grove_example_network/` and reads FleetPy's results from
  `studies/example_study/results/`. Both are git-ignored.
- FleetPy runs in the same Python process as MTSM (see `fleetpy_runner.py` for why).

## Local changes to code

| File | Change | Why |
|---|---|---|
| `src/demand/TravelerModels.py:74` | `.iteritems()` → `.items()` (old line kept as a comment) | pandas 2 removed `Series.iteritems` |
| `src/misc/config.py:126` | `pd.read_csv(..., squeeze=True)` → `pd.read_csv(...).squeeze("columns")` (old line kept as a comment) | pandas 2 removed `squeeze=` |
| `src/evaluation/standard.py:132` | same as above | same |
| `src/simulation/Vehicles.py:44` | same as above | same |
| `run_examples.py` | `import csv` added (unused); `.astype(object)` added in `read_outputs_for_comparison` (line 157); examples b) to j) commented out, so only example a) runs | avoids a pandas dtype warning in `check_assertions`; only the first example was needed |

The model's environment has pandas 2.2.3 (`env/`), so the four pandas changes are required.

Removed on 2026-11-07 (they were commented-out debug prints, no effect): extra lines in `src/FleetSimulationBase.py`,
`src/routing/NetworkBasic.py`, `src/routing/routing_imports/Router.py` and two in `run_examples.py`. These three
`src/` files are now identical to upstream.

`README.md` has one added line at the end (a command to run `src/evaluation/temporal.py`).

FleetPy's own example a) (`python run_examples.py` in this folder) runs, but serves 90 users where its check
expects 88 (I-12).

FleetPy's original `requirements.txt` (numpy 1.19.5, pandas 1.2.0, ...) is not in this folder. The repository root's
`requirements.txt` points to `env/`, the model's locked environment; the original list is in the git history
(commit `6d311ee`).

## Local changes to data

See `docs/open_issues.md`.

- **Vehicle types restored (2026-11-08):** `data/vehicles/default_vehtype.csv` and `low_range_vehtype.csv` had
  `maximum_passengers` changed from 4 to 8, because the Lemon Grove run used `default_vehtype`. Both are back to
  upstream. The model now has its own vehicle type, `lemon_grove_vehtype` (capacity 8), in
  `mtsm_data/lemon_grove/fleetpy_inputs/data/vehicles/`, copied into `data/vehicles/` before each run (I-09).
- **Added files still here** (not in upstream; none of them is read by the Lemon Grove run; I-11):
  - `data/demand/lemon_grove_example_demand/matched/lemon_grove_example_network/`: 69 old files;
  - `data/demand/example_demand/matched/example_network/`: 9 `lemon_grove_zonal_partition's effect on ...` plots;
  - `studies/example_study/scenarios/`: 13 old scenario configs whose study area is unknown,
    `example_ir_only_{5,10,15,20,30,40,50}_veh.csv` and `debug_example_ir_only*.csv` (6). They use
    `rq_file=fleetpy_demand.csv`, a name that existed in both the downtown and the Lemon Grove demand folder, and no
    code names them.
- **Downtown San Diego removed (2026-11-08):** the downtown configs had used FleetPy's `example_network` and
  `example_demand`, so FleetPy's example data had been overwritten. The 14 overwritten files (example network,
  demand `example_100/200/400`, initial vehicle distribution, depots, charging stations, zone mapping, 5 example
  configs) were restored from upstream `7019960`, byte for byte. Deleted: 283 downtown demand files (and plots),
  7 downtown network files, 33 downtown scenario configs (`downtown_sd_*` and `example_pool_1000_rq_*`), and 10
  files that only existed because the originals had been overwritten (`data/demand/example_demand_Munich/`,
  `node_zone_info_backup.csv`, `example_ir_heuristics_repositioning_origin.csv`). The last commit that has them is
  tagged `last-with-downtown-sd`.
- **Moved out of this folder (2026-11-07):** the Lemon Grove network (`data/networks/lemon_grove_example_network/`),
  its initial vehicle distribution and the 28 `lemon_grove_*` scenario configs, to
  `mtsm_data/lemon_grove/fleetpy_inputs/`.
