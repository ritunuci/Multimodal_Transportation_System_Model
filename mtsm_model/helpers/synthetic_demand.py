"""Synthetic microtransit requests for a run on a sample of the travelers (demand_upscaling; docs/open_issues.md I-32).

When the demand file is a sample, a share s of all travelers, FleetPy would serve only the sample's microtransit
requests, and the fleet would be less busy than with all travelers. add_synthetic_requests() therefore adds
(1 / s - 1) synthetic requests per request of the sample to FleetPy's demand file before FleetPy runs (3 for s = 0.25,
9 for s = 0.1). They are drawn from the sample's requests of the iteration: the time follows their time-of-day profile
within the microtransit operating periods, the origin-destination pair is one of theirs (in either direction). Their
only purpose is to make the fleet as busy as with all travelers: they are not travelers of MTSM (no trips, fares or
logsums), but FleetPy's waiting times, rejection rate and fleet results include them, as they should.

History: written by the user as synthesize_requests_with_trend_time (pre_process/generate_demand_files.py; moved here
unchanged on 2026-11-23, I-14), called by a commented-out "Ritun added" block in mtsm_model/microtransit.py: 3
synthetic requests per request (for a 25 % sample), ids from 60005, times 5:00-20:00, seed 42, appended after the
sample's rows. Since 2026-11-25 (I-32) it is the switch demand_upscaling of the run: the number comes from
demand_sample_share, the ids start above every traveler's (synthetic_id_start), the times lie in the scenario's
microtransit operating periods, the whole file is sorted by rq_time, and the seed is the run's random_seed. How the
times and pairs are drawn is unchanged (5-minute bins with a smoothing of 0.5 per bin; ordered pairs, reversed with
probability 0.5); reviewing it is I-45.
"""
import math
import sys
from typing import Optional

import numpy as np
import pandas as pd

FLEETPY_DEMAND_COLUMNS = ["rq_time", "start", "end", "request_id"]


def synthetic_id_start(traveler_ids, share):
    """The first request id of the synthetic requests: the smallest power of ten that is at least ten times the larger
    of (the largest traveler id + 1) and (the number of travelers / share, the size of the full demand). So the
    synthetic ids stay clear of every traveler's id, also of the travelers left out of the sample (as long as the full
    demand's ids stay below ten times that), and of the ids just above a traveler's own that MTSM gives to a second
    microtransit leg (trip_legs.free_request_id; add_synthetic_requests checks this in every iteration). Lemon Grove
    (3,742 travelers, ids up to 15,047, share 0.25): 1,000,000."""
    ids = list(traveler_ids)
    bound = max(max(ids) + 1, math.ceil(len(ids) / share))
    start = 1
    while start < 10 * bound:
        start *= 10
    return start


def make_time_sampler(rq_times, windows, bin_width: int = 300, alpha: float = 0.5,
                      rng: Optional[np.random.Generator] = None):
    """A sampler of request times (integer s) that follows the time-of-day profile of rq_times within the windows
    [(first, last)] (s, both included): each window is cut into bins of bin_width s (the last one may be shorter), a
    bin is drawn with probability (requests in it + alpha) / sum, and a time uniformly within it. Requests outside the
    windows are not counted. Returns sample_rq(n) -> np.ndarray of n times.
    (Until 2026-11-25 one window rq_min..rq_max, 18000..72000, with bins from rq_min.)"""
    if rng is None:
        rng = np.random.default_rng()
    lefts, rights = [], []
    for first, last in windows:
        for left in range(first, last + 1, bin_width):
            lefts.append(left)
            rights.append(min(left + bin_width - 1, last))
    if not lefts:
        raise ValueError("no time window for the synthetic requests")
    lefts = np.array(lefts, dtype=np.int64)
    rights = np.array(rights, dtype=np.int64)

    t = np.asarray(rq_times, dtype=float)
    counts = np.array([np.count_nonzero((t >= left) & (t < right + 1)) for left, right in zip(lefts, rights)],
                      dtype=float)
    # Laplace smoothing
    weights = counts + float(alpha)
    if weights.sum() <= 0:
        weights[:] = 1.0
    p = weights / weights.sum()

    def sample_rq(n):
        # choose bins according to observed frequencies, then sample uniformly within bin
        bin_idx = rng.choice(len(p), size=n, p=p)
        left = lefts[bin_idx]
        return left + rng.integers(0, rights[bin_idx] - left + 1, size=n, dtype=np.int64)

    return sample_rq


def make_od_sampler(starts, ends, preserve_od: bool = True, od_mode: str = "ordered", swap_prob: float = 0.5,
                    rng: Optional[np.random.Generator] = None):
    """A sampler of (start, end) node pairs from the observed pairs (starts[i], ends[i]). preserve_od True: draw an
    observed pair by its frequency and flip its direction with probability swap_prob; od_mode "ordered" counts (a, b)
    and (b, a) apart, "undirected" together (the direction then comes from swap_prob only). preserve_od False: start and
    end drawn independently from their own frequencies. Returns sample_od(n) -> (starts, ends).
    (Unchanged from synthesize_requests_with_trend_time, 2026-11-25.)"""
    if rng is None:
        rng = np.random.default_rng()
    starts = np.asarray(starts)
    ends = np.asarray(ends)

    if preserve_od:
        if od_mode not in ("undirected", "ordered"):
            raise ValueError("od_mode must be 'undirected' or 'ordered'")

        if od_mode == "undirected":
            # Build counts for unordered pairs (min(s,e), max(s,e))
            undirected = np.column_stack([np.minimum(starts, ends), np.maximum(starts, ends)])
            ud_df = pd.DataFrame(undirected, columns=["a", "b"])
            counts = ud_df.value_counts().reset_index(name="w")  # columns: a, b, w
            pairs = counts[["a", "b"]].to_numpy()
            weights = (counts["w"] / counts["w"].sum()).to_numpy()

            def sample_od(n):
                idx = rng.choice(len(pairs), size=n, p=weights)
                chosen = pairs[idx].copy()
                # Assign direction: with probability swap_prob, flip (a,b) -> (b,a)
                do_swap = rng.random(n) < swap_prob
                start_out = np.where(do_swap, chosen[:, 1], chosen[:, 0]).astype(int)
                end_out = np.where(do_swap, chosen[:, 0], chosen[:, 1]).astype(int)
                return start_out, end_out

        else:  # ordered
            od_df = pd.DataFrame({"start": starts, "end": ends}).groupby(["start", "end"]).size().reset_index(name="w")
            od_pairs = od_df[["start", "end"]].to_numpy()
            od_weights = (od_df["w"] / od_df["w"].sum()).to_numpy()

            def sample_od(n):
                idx = rng.choice(len(od_pairs), size=n, p=od_weights)
                chosen = od_pairs[idx].copy()
                do_swap = rng.random(n) < swap_prob
                start_out = np.where(do_swap, chosen[:, 1], chosen[:, 0]).astype(int)
                end_out = np.where(do_swap, chosen[:, 0], chosen[:, 1]).astype(int)
                return start_out, end_out

    else:
        # Independent marginals (doesn't preserve OD correlation)
        unique_s, cnt_s = np.unique(starts, return_counts=True)
        p_s = cnt_s / cnt_s.sum()
        unique_e, cnt_e = np.unique(ends, return_counts=True)
        p_e = cnt_e / cnt_e.sum()

        def sample_od(n):
            start_out = rng.choice(unique_s, size=n, p=p_s).astype(int)
            end_out = rng.choice(unique_e, size=n, p=p_e).astype(int)
            return start_out, end_out

    return sample_od


def synthesize_requests(df, n_new, first_id, windows, seed=None, preserve_od=True, od_mode="ordered", swap_prob=0.5,
                        bin_width=300, alpha=0.5):
    """n_new synthetic requests drawn from the requests df (columns rq_time, start, end): a DataFrame with the columns
    rq_time, start, end, request_id (first_id, first_id + 1, ...). Times: make_time_sampler within the windows; pairs:
    make_od_sampler. One generator, seeded with seed, draws first the times, then the pairs."""
    rng = np.random.default_rng(seed)
    sample_rq = make_time_sampler(df["rq_time"].to_numpy(), windows, bin_width=bin_width, alpha=alpha, rng=rng)
    sample_od = make_od_sampler(df["start"].to_numpy(), df["end"].to_numpy(), preserve_od=preserve_od,
                                od_mode=od_mode, swap_prob=swap_prob, rng=rng)
    new_rq = sample_rq(n_new)
    new_start, new_end = sample_od(n_new)
    return pd.DataFrame({
        "rq_time": new_rq,
        "start": new_start,
        "end": new_end,
        "request_id": np.arange(first_id, first_id + n_new, dtype=np.int64),
    })


def add_synthetic_requests(fleetpy_demand_file, share, id_start, windows, seed):
    """Add the synthetic requests of one iteration to FleetPy's demand file (written by iteration.run_iteration with
    the sample's microtransit legs): round(n x (1 / share - 1)) requests for its n requests, ids from id_start, times in
    the windows [(first, last)] (s; the microtransit operating periods). All rows are written sorted by rq_time (a
    stable sort): FleetPy takes the requests of one time step in the order of the file (I-32). Stops if a request id
    of the file reaches id_start. Returns (n, the number added)."""
    df = pd.read_csv(fleetpy_demand_file)
    if list(df.columns) != FLEETPY_DEMAND_COLUMNS:
        sys.exit(f"ERROR: {fleetpy_demand_file}: the columns must be {FLEETPY_DEMAND_COLUMNS}, not {list(df.columns)}")
    n_real = len(df)
    if n_real == 0:
        return 0, 0  # no microtransit request in the sample: nothing to draw from
    if int(df["request_id"].max()) >= id_start:
        sys.exit(f"ERROR: {fleetpy_demand_file}: request id {int(df['request_id'].max())} reaches the first id of the "
                 f"synthetic requests ({id_start}); synthetic_demand.synthetic_id_start must give a larger one")
    n_new = int(math.floor(n_real * (1 / share - 1) + 0.5))
    out = df
    if n_new > 0:
        new_df = synthesize_requests(df, n_new, id_start, windows, seed=seed)
        out = pd.concat([df, new_df], ignore_index=True)
    out = out.sort_values("rq_time", kind="mergesort")
    out.to_csv(fleetpy_demand_file, index=False)
    return n_real, n_new
