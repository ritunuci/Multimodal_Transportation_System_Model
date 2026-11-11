"""Entry point of the multimodal transportation system model (MTSM), Lemon Grove.

    python run_examples_new_parking.py                  the parameters of the frozen
                                                        mtsm_data/input_parameter/mtsm_constant_configurations.csv
    python run_examples_new_parking.py --config <file>  the parameters of <file> (a copy of the frozen file)

Reads the parameters and runs the model (mtsm_model/). The optimizer (Bayesian_optimization_script.py) starts this
script once per candidate, with --config and the candidate's copy. See README.md.
"""
import argparse
import os
import sys
import multiprocessing as mp
import datetime
import random

import numpy as np

# config.py reads the parameter file when it is imported, so --config reaches it in the environment variable
# MTSM_CONFIG_FILE (config.CONFIG_FILE_ENV), which the re-launched process below inherits. Without --config, a value
# left in the environment is removed: the run then always uses the frozen file.
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the MTSM (Lemon Grove).")
    parser.add_argument("--config", help="parameter file (default: the frozen mtsm_constant_configurations.csv)")
    args = parser.parse_args()
    if args.config:
        os.environ["MTSM_CONFIG_FILE"] = os.path.abspath(args.config)
    else:
        os.environ.pop("MTSM_CONFIG_FILE", None)

import mtsm_paths as mtsm
from mtsm_model import config
from mtsm_model.model import run_model

LOG_F = os.path.join(mtsm.CODE_ROOT, "standard_bugfix.log")  # FleetPy's log file


if __name__ == "__main__":
    mp.freeze_support()

    # Reproducibility (docs/progress.md, Phase 1): str hashing (set/dict order) is randomized per process unless
    # PYTHONHASHSEED is fixed before the interpreter starts -> re-launch once with a fixed hash seed and no
    # inherited PYTHONPATH (stale entries could shadow modules).
    if os.environ.get("PYTHONHASHSEED") != "0":
        import subprocess
        child_env = dict(os.environ, PYTHONHASHSEED="0")
        child_env.pop("PYTHONPATH", None)
        sys.exit(subprocess.call([sys.executable] + sys.argv, env=child_env))

    start_time = datetime.datetime.now()
    print("program starts here......start time is:", start_time)
    # the run's parameters are cfg.<name>; the model's constants are config.<NAME> (both from config.CONSTANT_CONFIG_FILE)
    cfg = config.read_run_config()
    config.check_run_config(cfg)

    random.seed(cfg.random_seed)
    np.random.seed(cfg.random_seed)
    print("random_seed:", cfg.random_seed, "PYTHONHASHSEED:", os.environ.get("PYTHONHASHSEED"))

    run_model(cfg, start_time, LOG_F)
