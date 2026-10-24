"""Lock files for the Python environment of the model run, in env/ (see docs/progress.md, Phase 2b).

    python tools/export_env.py           check the running environment against env/; exit code 1 if it differs
    python tools/export_env.py --write   (re)create env/ from the running environment -- only after a deliberate
                                         environment change, and record it in docs/progress.md

Run it with the environment's own interpreter (the fleetpy conda env). It writes:
    env/fleetpy.conda-explicit.txt   conda packages: exact URL + MD5 of every package (conda create --file)
    env/fleetpy.pip.txt              packages installed by pip (102 of them, e.g. pandas, gurobipy): name==version
    env/fleetpy.environment.yml      readable summary (conda env export --no-builds); not exact, not used by the check
    env/fleetpy.system.txt           what is outside the env: OS, CPU, conda, BLAS, Gurobi license (type and expiry
                                     only, never the key); for the record, not used by the check
"""
import importlib.metadata as md
import os
import platform
import shutil
import subprocess
import sys

CODE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_DIR = os.path.join(CODE_ROOT, "env")
NAME = "fleetpy"
CONDA_FILE = os.path.join(ENV_DIR, NAME + ".conda-explicit.txt")
PIP_FILE = os.path.join(ENV_DIR, NAME + ".pip.txt")
YML_FILE = os.path.join(ENV_DIR, NAME + ".environment.yml")
SYSTEM_FILE = os.path.join(ENV_DIR, NAME + ".system.txt")
# license file fields that are safe to record (KEY, USERNAME, HOSTNAME etc. are left out)
LICENSE_FIELDS = ("TYPE", "VERSION", "EXPIRATION")


def conda_exe():
    exe = os.environ.get("CONDA_EXE") or shutil.which("conda")
    if not exe:
        sys.exit("conda not found (set CONDA_EXE or put conda on PATH)")
    return exe


def conda(*args):
    return subprocess.run([conda_exe(), *args, "-p", sys.prefix], check=True, capture_output=True, text=True).stdout


def gurobi_license():
    """(location, {field: value}) of the Gurobi license file gurobipy finds first, or (None, {})"""
    for path in (os.environ.get("GRB_LICENSE_FILE"), os.path.join(os.path.expanduser("~"), "gurobi.lic"),
                 r"C:\gurobi\gurobi.lic"):
        if path and os.path.isfile(path):
            fields = {}
            with open(path) as f:
                for line in f:
                    k, _, v = line.strip().partition("=")
                    if k.strip().upper() in LICENSE_FIELDS:
                        fields[k.strip().upper()] = v.strip()
            return path, fields
    return None, {}


def system_lines():
    blas = [l.rsplit("/", 1)[-1].split("#")[0] for l in conda_lines() if "/mkl-" in l or "openblas" in l]
    lic_path, lic = gurobi_license()
    return [
        "# what the model run depends on outside the Python packages (written by tools/export_env.py --write)",
        f"os: {platform.platform()} ({platform.machine()})",
        f"cpu: {platform.processor()}, {os.cpu_count()} logical CPUs",
        f"python: {sys.version.split()[0]} ({sys.prefix})",
        f"conda: {subprocess.run([conda_exe(), '--version'], capture_output=True, text=True).stdout.strip()}",
        f"blas: {', '.join(blas) or 'see conda file'}",
        f"gurobipy: {md.version('gurobipy')}",
        "gurobi license file: " + (os.path.basename(lic_path) + " in " + os.path.dirname(lic_path) if lic_path else "none found"),
        "gurobi license: " + (", ".join(f"{k}={lic[k]}" for k in LICENSE_FIELDS if k in lic) or "-"),
    ]


def conda_lines():
    """explicit conda package list (URL#md5), as conda prints it"""
    return conda("list", "--explicit", "--md5").splitlines()


def pip_lines():
    """name==version of every package pip installed (conda's own packages are in the conda file)"""
    pins = {d.metadata["Name"]: d.version for d in md.distributions()
            if (d.read_text("INSTALLER") or "").strip() == "pip"}
    return [f"{n}=={v}" for n, v in sorted(pins.items(), key=lambda kv: kv[0].lower())]


def packages(lines):
    """the package entries of a lock file (no comments, no @EXPLICIT marker)"""
    return {l.strip() for l in lines if l.strip() and not l.startswith(("#", "@"))}


def write(path, lines):
    with open(path, "w", newline="\r\n") as f:
        f.write("\n".join(lines) + "\n")


def write_env():
    os.makedirs(ENV_DIR, exist_ok=True)
    c, p = conda_lines(), pip_lines()
    write(CONDA_FILE, c)
    write(PIP_FILE, [f"# packages installed by pip into the {NAME} env (Python {sys.version.split()[0]});",
                     "# install after the conda file: pip install --no-deps -r env/" + os.path.basename(PIP_FILE)] + p)
    yml = [l for l in conda("env", "export", "--no-builds").splitlines() if not l.startswith("prefix:")]
    write(YML_FILE, [f"name: {NAME}" if l.startswith("name:") else l for l in yml])
    write(SYSTEM_FILE, system_lines())
    print(f"wrote {ENV_DIR}: {len(packages(c))} conda packages, {len(p)} pip packages, system info")


def check_env():
    """returns a list of differences between the running environment and env/ (empty = same)"""
    problems = []
    for path, current in ((CONDA_FILE, conda_lines()), (PIP_FILE, pip_lines())):
        if not os.path.isfile(path):
            problems.append(f"lock file missing: {path}")
            continue
        with open(path) as f:
            locked = packages(f)
        now = packages(current)
        problems += [f"{os.path.basename(path)}: not installed: {x}" for x in sorted(locked - now)]
        problems += [f"{os.path.basename(path)}: not in lock: {x}" for x in sorted(now - locked)]
    return problems


if __name__ == "__main__":
    if "--write" in sys.argv:
        write_env()
    else:
        problems = check_env()
        print("\n".join(problems) if problems else f"environment {sys.prefix} matches {ENV_DIR}")
        sys.exit(1 if problems else 0)
