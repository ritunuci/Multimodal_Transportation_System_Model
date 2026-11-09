"""Entry point of the multimodal transportation system model (MTSM), Lemon Grove.

Reads the run's parameters (mtsm_data/input_parameter/input_parameter.csv) and runs the model (mtsm_model/). The
optimizer (Bayesian_optimization_script.py) starts this script once per candidate. See README.md.
"""
import os
import sys
import multiprocessing as mp
import datetime
import random

import numpy as np

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
    # the run's parameters (input_parameter.csv) are cfg.<name>; the model's constants are config.<NAME>
    cfg = config.read_run_config()
    config.check_run_config(cfg)

    random.seed(cfg.random_seed)
    np.random.seed(cfg.random_seed)
    print("random_seed:", cfg.random_seed, "PYTHONHASHSEED:", os.environ.get("PYTHONHASHSEED"))

    run_model(cfg, start_time, LOG_F)
