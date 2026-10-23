"""Compare the outputs of the last run with the stored reference outputs, byte by byte.

    python tools/compare_reference.py [reference_name]      default reference_name: lemon_grove_seed0

Run it after a full run with the reference's input (mtsm/, checked by tools/check_inputs.py) and seed. Every
reference file must be byte-identical; anything else means the code change altered the results.
Exception: FleetPy's 00_config.json records the absolute location of the codebase, so in that file the code root is
replaced by a placeholder on both sides before comparing.
Exit code 0 = identical, 1 = differences or missing files.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mtsm_paths as mtsm

# reference sub-folder -> folder the run writes that file to
LOCATIONS = {
    "output": mtsm.LG_OUTPUT_DIR,
    "intermediate/final_network": mtsm.LG_FINAL_NETWORK_DIR,
    "intermediate/initial_network": mtsm.LG_INITIAL_NETWORK_DIR,
    "intermediate/initial_network_0719": mtsm.LG_INITIAL_NETWORK_0719_DIR,
    "intermediate/indiv_output": mtsm.LG_INDIV_OUTPUT_DIR,
    "intermediate/fleetpy_demand": mtsm.LG_FLEETPY_DEMAND_DIR,
    "intermediate/fleetpy_results": os.path.join(mtsm.FLEETPY_RESULTS_DIR, "example_pool_repo_AM_sc_1"),
}
LOCATION_DEPENDENT = {"00_config.json"}
REFERENCE_CODE_ROOT = r"D:\Ritun\Siwei_Micro_Transit\FleetPy_SanDiego"  # where the reference run was made


def _normalized(data, code_root):
    escaped = code_root.replace("\\", "\\\\").encode()  # paths are JSON-escaped in 00_config.json
    return data.replace(escaped, b"<CODE_ROOT>")


def compare(reference_name="lemon_grove_seed0"):
    ref_root = os.path.join(mtsm.CODE_ROOT, "docs", "reference_results", reference_name)
    n_same, problems = 0, []
    for sub, live_dir in LOCATIONS.items():
        ref_dir = os.path.join(ref_root, *sub.split("/"))
        for name in sorted(os.listdir(ref_dir)):
            live = os.path.join(live_dir, name)
            if not os.path.isfile(live):
                problems.append(f"MISSING  {sub}/{name}  (expected at {live})")
                continue
            with open(os.path.join(ref_dir, name), "rb") as f:
                ref_data = f.read()
            with open(live, "rb") as f:
                live_data = f.read()
            if name in LOCATION_DEPENDENT:
                ref_data, live_data = _normalized(ref_data, REFERENCE_CODE_ROOT), _normalized(live_data, mtsm.CODE_ROOT)
            if ref_data == live_data:
                n_same += 1
                continue
            ref_lines, live_lines = ref_data.splitlines(), live_data.splitlines()
            first = next((i for i, (a, b) in enumerate(zip(ref_lines, live_lines)) if a != b),
                         min(len(ref_lines), len(live_lines)))
            problems.append(f"DIFFERS  {sub}/{name}  (first difference at line {first + 1}; "
                            f"{len(ref_lines)} vs {len(live_lines)} lines)")
    return n_same, problems


if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else "lemon_grove_seed0"
    n_same, problems = compare(name)
    print("\n".join(problems))
    print(f"{n_same} identical, {len(problems)} differing/missing -> "
          f"{'REPRODUCED' if not problems else 'NOT REPRODUCED'} ({name})")
    sys.exit(1 if problems else 0)
