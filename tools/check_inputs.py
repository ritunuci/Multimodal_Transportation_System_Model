"""Verify the frozen inputs in mtsm_data/ against their manifests (size + SHA-256).

Since 2026-11-24 (docs/study_area_plan.md, Phase 1 decision 3) there is one manifest per study area:
- mtsm_data/MANIFEST.csv: the shared model parameter file;
- mtsm_data/<area>/MANIFEST.csv: the study area's inputs (docs/study_area_inputs.md). Optional: an area without one is
  not checked. Until 2026-11-24 mtsm_data/MANIFEST.csv listed the Lemon Grove inputs too.
Paths in a manifest are relative to the manifest's folder, "/" separated.

    python tools/check_inputs.py                check the shared manifest and every area manifest; exit code 1 if any
                                                input is missing or changed
    python tools/check_inputs.py --write AREA   (re)write the shared manifest and AREA's manifest from the current
                                                files -- only after a deliberate input change, and record it in
                                                docs/progress.md
"""
import csv
import glob
import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mtsm_paths import MTSM_DIR, area_paths

MANIFEST = os.path.join(MTSM_DIR, "MANIFEST.csv")

# shared frozen input -> role; paths relative to mtsm_data/
SHARED_INPUTS = {
    "input_parameter/mtsm_constant_configurations.csv": "all MTSM parameters (model file)",
}

FLEETPY_ROLES = {  # file name ending -> role, for AreaPaths.fleetpy_staged
    "/base/nodes.csv": "FleetPy road network nodes",
    "/base/edges.csv": "FleetPy road network edges",
    "/base/crs.info": "FleetPy network coordinate system",
    "/imbalanced.csv": "FleetPy initial vehicle distribution",
    "_vehtype.csv": "FleetPy vehicle type",
}


def area_inputs(area):
    """{path relative to mtsm_data/<area>/: role}: the inputs of a study area that exist (docs/study_area_inputs.md),
    plus every FleetPy config file in the area's scenarios folder."""
    paths = area_paths(area)

    def rel(p):
        return os.path.relpath(p, paths.dir).replace(os.sep, "/")

    candidates = [(paths.area_parameter_file, "area parameter file (file 1)"),
                  (paths.demand_file, "travel demand (file 2)")]
    candidates += [(f, "super-network with microtransit (file 3)")
                   for f in sorted(glob.glob(os.path.join(paths.networks_dir, "super_network_micro_virstop_*.csv")))]
    candidates += [(paths.super_network_frt_file, "FRT-only super-network (file 4)"),
                   (paths.car_network_file, "car network (file 5)"),
                   (paths.frt_links_file, "FRT links (file 6)"),
                   (paths.frt_routes_file, "FRT route table (file 10)"),
                   (paths.nodes_file, "node file (file 7, optional)"),
                   (paths.super_network_frt_base_headway_file, "FRT-only super-network at the base headway (file 9)")]
    for staged in paths.fleetpy_staged:
        role = next(r for end, r in FLEETPY_ROLES.items() if staged.endswith(end))
        candidates.append((os.path.join(paths.fleetpy_inputs_dir, *staged.split("/")), role))
    for f in sorted(glob.glob(os.path.join(paths.fleetpy_scenarios_dir, "*.csv"))):
        role = "FleetPy constant config" if "_constant_config_" in os.path.basename(f) else "FleetPy scenario config"
        candidates.append((f, role))
    return {rel(p): role for p, role in candidates if os.path.isfile(p)}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _write(manifest, folder, inputs):
    with open(manifest, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["path", "size_bytes", "sha256", "role"])
        for rel, role in inputs.items():
            p = os.path.join(folder, *rel.split("/"))
            w.writerow([rel, os.path.getsize(p), sha256(p), role])
    print(f"wrote {manifest} ({len(inputs)} inputs)")


def write_manifest(area):
    _write(MANIFEST, MTSM_DIR, SHARED_INPUTS)
    paths = area_paths(area)
    _write(paths.manifest_file, paths.dir, area_inputs(area))


def _check(manifest, folder):
    label = os.path.relpath(folder, MTSM_DIR).replace(os.sep, "/")
    prefix = "" if label == "." else label + "/"
    problems = []
    with open(manifest, newline="") as f:
        for row in csv.DictReader(f):
            p = os.path.join(folder, *row["path"].split("/"))
            if not os.path.isfile(p):
                problems.append(f"missing: {prefix}{row['path']}")
            elif os.path.getsize(p) != int(row["size_bytes"]) or sha256(p) != row["sha256"]:
                problems.append(f"changed: {prefix}{row['path']}")
    return problems


def check_inputs(areas=None):
    """Returns a list of problems (empty = all frozen inputs unchanged). areas: the study areas whose manifests are
    checked (an area without a manifest is skipped); None = every area folder with a manifest."""
    if not os.path.isfile(MANIFEST):
        return [f"manifest missing: {MANIFEST}"]
    problems = _check(MANIFEST, MTSM_DIR)
    if areas is None:
        areas = sorted(os.path.basename(os.path.dirname(m)) for m in glob.glob(os.path.join(MTSM_DIR, "*", "MANIFEST.csv")))
    for area in areas:
        paths = area_paths(area)
        if os.path.isfile(paths.manifest_file):
            problems += _check(paths.manifest_file, paths.dir)
    return problems


if __name__ == "__main__":
    if "--write" in sys.argv:
        args = [a for a in sys.argv[1:] if a != "--write"]
        if len(args) != 1:
            sys.exit("usage: python tools/check_inputs.py --write AREA")
        write_manifest(args[0])
    else:
        problems = check_inputs()
        print("\n".join(problems) if problems else "all frozen inputs match their manifests")
        sys.exit(1 if problems else 0)
