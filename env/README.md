# Python environment

Lock files of the `fleetpy` conda env that the reference results (`docs/reference_results/`) were produced with:
Python 3.10.19 on Windows 10 (win-64). Written by `python tools/export_env.py --write`; see `docs/progress.md`, Phase 2b.
A machine also needs what is listed under "Outside the environment" below, in particular a valid Gurobi license.

| File | Content | Exact? |
|---|---|---|
| `fleetpy.conda-explicit.txt` | the 34 conda packages: download URL and MD5 of each build | yes (win-64 only) |
| `fleetpy.pip.txt` | the 102 packages pip installed (pandas, gurobipy, networkx, torch, ax-platform, ...): `name==version` | versions yes, wheel hashes no |
| `fleetpy.environment.yml` | readable summary from `conda env export --no-builds` | no; for reading or other platforms |
| `fleetpy.system.txt` | what is outside the env: OS, CPU, conda, BLAS, Gurobi license type and expiry | record only |

## Outside the environment

What the lock files cannot pin (recorded in `fleetpy.system.txt` as of the last `--write`):

- **OS / CPU**: Windows 10 (10.0.19045, 64-bit), Intel CPU with 12 logical CPUs. The conda file is win-64 only.
- **Math library**: numpy/scipy use Intel MKL 2024.2.2 (pinned in the conda file). MKL may pick different code
  paths on different CPUs, which can change floating-point results in the last digits. If a second machine does not
  reproduce, try setting `MKL_CBWR=COMPATIBLE` before the run (and on the reference machine, to compare).
- **Gurobi license** (not part of any package): an `ACADEMIC` license for Gurobi 12 in `gurobi.lic` in the user's home
  folder; it is per user and machine, so every machine needs its own (academic: request one at gurobi.com and install
  it with `grbgetkey`). The license key is never stored in this repository.
  - **The license on the reference machine expired on 2026-10-21.**
  - The reference run is not affected: Gurobi is used only by AlonsoMora repositioning, and only when a request was
    rejected since the last repositioning step. In the reference scenario, all 68 requests in each of the 5 iterations
    were served, so Gurobi is never started.
  - A parameter set that does lead to rejections (e.g. a smaller fleet, or an optimizer candidate) stops with
    `GurobiError: License expired` until the license is renewed.
- **Threads**: FleetPy runs with `n_cpu_per_sim = 1`, so a Gurobi solve uses one thread (deterministic).

## Recreate the environment

From the repository root (any env name works; the model run does not depend on it):

    conda create -n fleetpy --file env/fleetpy.conda-explicit.txt
    conda activate fleetpy
    pip install --no-deps -r env/fleetpy.pip.txt
    python tools/export_env.py

The last command must print `environment ... matches ...`. `--no-deps` installs exactly the locked set; the lock is
complete (`pip check` reported no broken requirements when it was written).

## Check an existing environment

    python tools/export_env.py

It compares the running interpreter's environment with the lock files and lists every package that is missing or
not in the lock (exit code 1 if anything differs).
