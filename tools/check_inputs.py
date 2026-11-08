"""Verify the frozen inputs in mtsm_data/ against mtsm_data/MANIFEST.csv (size + SHA-256).

    python tools/check_inputs.py           check; exit code 1 if any input is missing or changed
    python tools/check_inputs.py --write   (re)create the manifest from the current files -- only after a
                                           deliberate input change, and record it in docs/progress.md
"""
import csv
import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mtsm_paths import MTSM_DIR

MANIFEST = os.path.join(MTSM_DIR, "MANIFEST.csv")

# frozen input -> role; paths relative to mtsm_data/, "/" separated
INPUTS = {
    "input_parameter/input_parameter.csv": "scenario parameters",
    "region/pre_nodes.csv": "region road nodes",
    "region/final_land_use.csv": "land use (employment)",
    "region/activitysim_output/lemon_grove_MGRA_pop_inc.csv": "MGRA population / income",
    "region/activitysim_output/lemon_grove_MGRA_adj.csv": "MGRA adjacency",
    "lemon_grove/demand_data/lemon_grove_trips_nodes_study_area_with_beta.csv": "travel demand (agents)",
    "lemon_grove/initial_network/auto_edges.csv": "auto network",
    "lemon_grove/initial_network/base_super_network_lemon_grove_micro_hw_10_virstop_75.csv": "base super-network (micro)",
    "lemon_grove/initial_network/base_super_network_lemon_grove_non_micro_hw_10.csv": "base super-network (fixed route)",
    "lemon_grove/initial_network/initial_super_network_non_micro_hw_20.csv": "fixed-route network, base headway 20",
    "lemon_grove/initial_network_0719/initial_super_network_micro_hw_20_virstop_100.csv": "node list for accessibility",
    "lemon_grove/transit/super_network_transit_edges.csv": "transit edges",
    "lemon_grove/transit/network_folder/pre_nodes.csv": "lemon_grove road nodes",
    "lemon_grove/transit/mgra_node_mapping/Nodes_MGRA_mapping.csv": "node -> MGRA mapping",
    # inputs FleetPy reads; copied into fleetpy/ before each FleetPy run (fleetpy_runner.stage_inputs)
    "lemon_grove/fleetpy_inputs/data/networks/lemon_grove_example_network/base/nodes.csv": "FleetPy road network nodes",
    "lemon_grove/fleetpy_inputs/data/networks/lemon_grove_example_network/base/edges.csv": "FleetPy road network edges",
    "lemon_grove/fleetpy_inputs/data/networks/lemon_grove_example_network/base/crs.info": "FleetPy network coordinate system",
    "lemon_grove/fleetpy_inputs/data/fleetctrl/initial_vehicle_distribution/lemon_grove_example_network/imbalanced.csv":
        "FleetPy initial vehicle distribution",
    "lemon_grove/fleetpy_inputs/studies/example_study/scenarios/lemon_grove_constant_config_ir_repo.csv": "FleetPy constant config",
    "lemon_grove/fleetpy_inputs/studies/example_study/scenarios/lemon_grove_example_ir_heuristics_repositioning_2_veh.csv":
        "FleetPy scenario config (fleet size 2)",
}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def write_manifest():
    with open(MANIFEST, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["path", "size_bytes", "sha256", "role"])
        for rel, role in INPUTS.items():
            p = os.path.join(MTSM_DIR, rel)
            w.writerow([rel, os.path.getsize(p), sha256(p), role])
    print(f"wrote {MANIFEST} ({len(INPUTS)} inputs)")


def check_inputs():
    """returns a list of problems (empty = all frozen inputs unchanged)"""
    if not os.path.isfile(MANIFEST):
        return [f"manifest missing: {MANIFEST}"]
    problems = []
    with open(MANIFEST, newline="") as f:
        for row in csv.DictReader(f):
            p = os.path.join(MTSM_DIR, row["path"])
            if not os.path.isfile(p):
                problems.append(f"missing: {row['path']}")
            elif os.path.getsize(p) != int(row["size_bytes"]) or sha256(p) != row["sha256"]:
                problems.append(f"changed: {row['path']}")
    return problems


if __name__ == "__main__":
    if "--write" in sys.argv:
        write_manifest()
    else:
        problems = check_inputs()
        print("\n".join(problems) if problems else f"all frozen inputs match {MANIFEST}")
        sys.exit(1 if problems else 0)
