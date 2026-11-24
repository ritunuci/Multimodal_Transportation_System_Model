"""Synthetic microtransit requests that follow the observed time-of-day trend and OD structure: added to
FleetPy's demand file by the commented-out "Ritun added" block in mtsm_model/microtransit.py (imported there as
syn_rq; not called by the run; see docs/open_issues.md, I-32).

Moved unchanged from pre_process/generate_demand_files.py on 2026-11-23 (I-14), so that the run imports nothing
from pre_process/."""
from typing import Optional

import numpy as np
import pandas as pd
from colorama import Fore, Style


############################################# Ritun added (for FleetPy deamnd upscaling) #############################################
def make_time_sampler(df: pd.DataFrame,
                      rq_min: int = 18000,
                      rq_max: int = 72000,
                      bin_width: int = 300,
                      alpha: float = 0.5,
                      rng: Optional[np.random.Generator] = None
    ):
    """
    Build a sampler that follows the observed intraday distribution of rq_time
    within [rq_min, rq_max] using a histogram.

    Parameters
    ----------
    rq_min, rq_max : int
        Bounds in seconds since midnight (inclusive).
    bin_width : int
        Bin width in seconds (e.g., 300 = 5 min).
    alpha : float
        Laplace smoothing per bin to avoid zero-probability bins.
    rng : np.random.Generator | None
        RNG to use. If None, a new Generator is created.

    Returns
    -------
    sample_rq(n: int) -> np.ndarray[int]
        Function that samples n integer rq_time values following the observed trend.
    """
    if rng is None:
        rng = np.random.default_rng()

    rq_vals = df.loc[
        (df["rq_time"] >= rq_min) & (df["rq_time"] <= rq_max),
        "rq_time"
    ].to_numpy()

    if rq_vals.size == 0:
        # Fallback: uniform if no data in window
        def sample_rq(n):
            return rng.integers(rq_min, rq_max + 1, size=n, dtype=np.int64)

        return sample_rq

    # Histogram edges and counts
    edges = np.arange(rq_min, rq_max + bin_width, bin_width, dtype=int)
    hist, edges = np.histogram(rq_vals, bins=edges)

    # Laplace smoothing
    weights = hist.astype(float) + float(alpha)
    if weights.sum() <= 0:
        weights[:] = 1.0
    p = weights / weights.sum()

    def sample_rq(n):
        # choose bins according to observed frequencies, then sample uniformly within bin
        bin_idx = rng.choice(len(p), size=n, p=p)
        left = edges[bin_idx]
        right = np.minimum(edges[bin_idx + 1] - 1, rq_max)  # inclusive
        # uniform integer within [left, right]
        return left + rng.integers(0, (right - left + 1), size=n, dtype=np.int64)

    return sample_rq

def synthesize_requests_with_trend_time(
    input_csv: str,
    output_csv: str,
    n_new: int,
    count: int,
    seed: Optional[int] = None,
    preserve_od: bool = True,
    od_mode: str = "undirected",   # "undirected" (pair strength, random direction) or "ordered"
    swap_prob: float = 0.5,         # chance to flip direction when preserve_od=True
    rq_min: int = 18000,           # 5:00 AM
    rq_max: int = 72000,           # 8:00 PM
    bin_width: int = 300,           # 5-minute bins for trend
    alpha: float = 0.5              # Laplace smoothing per time bin
):
    """
        Generate n_new synthetic requests:
          • rq_time: integers sampled to match the observed intraday trend (peaks/off-peaks) within [rq_min, rq_max]
          • start/end: sampled from observed OD structure (with optional direction swapping), or independent marginals
          • request_id: starts at (count + 5) and increments by 1

        Parameters
        ----------
        input_csv : str
            Path to existing CSV with columns: rq_time, start, end, request_id (others ignored).
        output_csv : str
            Path to write the augmented CSV (original + new).
        n_new : int
            Number of new rows to generate.
        count : int
            First new request_id will be (count + 5).
        seed : int | None
            RNG seed for reproducibility.
        preserve_od : bool
            If True, sample start/end from observed OD structure.
        od_mode : {"undirected","ordered"}
            - "undirected": collapse OD pairs into unordered (min,max) with weights; assign direction randomly (swap_prob).
            - "ordered": use observed ordered (start,end) weights; allow swapping with swap_prob to create reverse flows.
        swap_prob : float
            Probability to flip direction of sampled pair when preserve_od=True.
        rq_min, rq_max : int
            Time window in seconds since midnight (inclusive).
        bin_width : int
            Histogram bin width for time-of-day trend.
        alpha : float
            Laplace smoothing per time bin.
        """
    rng = np.random.default_rng(seed)

    df = pd.read_csv(input_csv, dtype={"rq_time": int, "start": int, "end": int, "request_id": int})
    if not {"rq_time", "start", "end"}.issubset(df.columns):
        raise ValueError("input_csv must contain columns: rq_time, start, end")

    # ---- rq_time sampler that follows observed trend ----
    sample_rq = make_time_sampler(
        df, rq_min=rq_min, rq_max=rq_max, bin_width=bin_width, alpha=alpha, rng=rng
    )

    # ----------------- OD samplers -----------------
    starts = df["start"].to_numpy()
    ends = df["end"].to_numpy()

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
            od_df = df.groupby(["start", "end"]).size().reset_index(name="w")
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

    # ----------------- Generate new rows -----------------
    new_rq = sample_rq(n_new)
    new_start, new_end = sample_od(n_new)
    new_request_ids = np.arange(count + 5, count + 5 + n_new, dtype=int)

    new_df = pd.DataFrame({
        "rq_time": new_rq,
        "start": new_start,
        "end": new_end,
        "request_id": new_request_ids,
    })

    # Concatenate and write
    out = pd.concat([df, new_df], ignore_index=True)
    out.to_csv(output_csv, index=False)
    print(f"{Fore.RED}Total demand in FleetPy (from demand generator): {len(out)}{Style.RESET_ALL}")
    return new_df  # return only the newly created block for quick inspection
#######################################################################################################
