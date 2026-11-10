# Plan: speed up the least-cost path search (`generalized_cost_dijsktra_OD_heap`)

Status: **done (2026-11-10).** The user's answers are under "Decisions needed"; result and verification under
"Result" and in `docs/progress.md`, "Faster least-cost path search". Written 2026-11-09. The code and line numbers
refer to `network_algorithms.py` after the cleanup of 2026-11-09 (commit `d7562c5`).

Scope (the user's decision): only the function `network_algorithms.generalized_cost_dijsktra_OD_heap`. Other ways to
cut the run time (for example, fewer calls) are not part of this plan.

## Why: the function takes 86% of the run time

Measured with one full seed-0 run, with wall-clock timers wrapped around the main stages from outside (no repository
file changed; the outputs matched the reference, `REPRODUCED`):

| Stage | Seconds | Share | Calls |
|---|---:|---:|---:|
| **Least-cost path search (`generalized_cost_dijsktra_OD_heap`)** | **926** | **86%** | 67,356 |
| Rest of each iteration (mode choice, bookkeeping) | 55 | 5% | |
| FleetPy simulation | 46 | 4% | 5 |
| Writing the results after convergence | 37 | 3% | 1 |
| Reading the networks | 3 | 0.3% | 35 |
| Building the path trajectories (`getTrajectory_O_to_D`) | 1 | 0.1% | 112,260 |
| **Whole run** | **1,077** | | |

The run has 3,742 travelers and 6 iterations. Each traveler gets 3 searches per iteration (car, FRT and microtransit),
67,356 calls in all, about 14 ms each. By network:

| Network | Nodes / links | Seconds | ms per call |
|---|---|---:|---:|
| With microtransit | 2,269 / 7,518 | 429 | 20.6 |
| FRT only | 1,170 / 3,080 | 268 | 11.1 |
| Car | 1,099 / 2,808 | 230 | 10.2 |

A search reaches only about 500–900 nodes before it finds the destination. The time is Python overhead per node, not
network size.

## Where the time goes inside the function

Profiled (cProfile) on 1,125 calls: every 10th traveler (375) × car, FRT and microtransit, on the reference inputs
(the microtransit network was the final AM network). This only read the input files. One call does about 760 heap
pushes and 605 pops. Without the profiler the 1,125 calls took 15.8 s (14 ms each, the same as in the full run).

| Part of the function | Share of the profiled time |
|---|---:|
| `get_link_type_from_O_to_D`, called once per node taken from the heap | **42%** |
| The function's own loop body (bookkeeping, 6 cost dicts and 3 path dicts) | 34% |
| `graph.get_edge_data(...)`, called 4 times per link | 7% |
| The rest of networkx's adjacency lookup | about 4% |
| Heap operations and `Heap_Node.__lt__` | about 15% |

`get_link_type_from_O_to_D` walks the path back to the origin every time a node comes off the heap. It does this only
to find two flags: has the path used a microtransit link (link type 4: `IsMicroLink`) or an FRT link (link type 1:
`IsFixedLink`)? Its third return value (the trajectory) is not used.

## Facts the plan relies on (checked 2026-11-09)

- **No link can cost less than zero.**
  - All 11 coefficients (`bt_c_0`, `bt_c_ivt`, `bt_c_gas`, `bt_t_0`, `bt_t_wk`, `bt_m_wt`, `bt_f_wt`, `bt_m_ivt`,
    `bt_f_ivt`, `bt_f_trfer`, `bt_t_fr`) are ≥ 0 for all 3,742 travelers.
  - No link has a negative travel time or length (car, FRT and microtransit networks).
  - Fares and fare factors are ≥ 0.

  So once a node comes off the heap with its least cost, its cost and path never change again.
- **Callers use only part of the result.** `mtsm_model/choice.py` reads the values at the destination; `paths.py`
  builds the origin-to-destination trajectory from the path dicts (`getTrajectory_O_to_D`).
- **Ties.** Equal costs are ordered by `Heap_Node.__lt__`, which compares the cost only; on a tie, the heap's internal
  order decides. The changes below keep the same pushes in the same order, so ties come out the same.
- **State carried between links.** `transit_fare` is reset to 0 after every link in transit mode, and `micro_fare` /
  `gas_cost` are set for every link. A link's cost therefore depends only on (node, next node, the path's two flags),
  so processing a settled node again computes the same costs.
- The run's agents are read once (`read_request`) and never changed.
- Link types per network: car {7}; FRT {0, 1, 2}; microtransit {0, 1, 2, 4, 5}.

## The changes (in `network_algorithms.py` only; same signature and return values)

1. **Carry the two flags along the path instead of walking back.** When a node's path is set
   (`path[edge] = (min_node, ...)`), store its flags: those of the node it was reached from, plus the link just used
   (type 4 sets `IsMicroLink`, type 1 sets `IsFixedLink`). This replaces the call to `get_link_type_from_O_to_D`,
   which nothing else in the model uses (decision 2). The flags are exactly what the walk-back finds, because a node's
   path is fixed once it comes off the heap. Expected saving: about 40%.
2. **Skip nodes already settled.** At present, an outdated heap entry of a node is processed again. That repeat cannot
   change anything: it computes the same costs, and an update needs a strictly smaller one (`temp < visited_temp[edge]`).
   Skipping it therefore leaves the pushes and the heap exactly as they are now.
3. **Look up each link once.** Build, once per network, a list per node of (to-node, travel time, link type, length,
   route), in the same order networkx gives today. Store it on the graph object (for example `graph.graph[...]`); the
   networks are re-read every iteration, so the list is rebuilt with them. This replaces the four `get_edge_data` calls
   and the networkx view per link.
4. **Remove the `try`/`except` block that builds an unused set of all nodes on every call.** It was kept unchanged in
   the cleanup; it is in scope now.
5. **Move `Heap_Node` out of the function and add `__slots__`.** It is currently re-created on every call. Its
   comparison stays exactly as it is.

The arithmetic stays exactly as written; for example, `bt_t_wk * link_travel_time / 60` is not rewritten, because a
different order of operations can change the last digit. The quirks stay too (for example, car mode pushes the origin
with `bt_t_0` but stores `bt_c_0`; the `WAITING LINK` print).

Side effect on the console only: the debug line `WAITING LINK = 180` (iterations after the first) can appear fewer
times, because outdated heap entries are no longer processed again. No output file changes; the reference run prints
it 0 times.

## What not to do, and why

- **Heap entries as `(cost, counter, node)` tuples, a scipy or networkx shortest-path routine, or A* / bidirectional
  search:** these break ties differently, so the results would no longer be byte-identical. The library routines also
  can't model the path-dependent transfer discounts.
- **Numba or Cython:** a new dependency, and a much larger change for this step.

## Checks

1. **Equivalence test (scratchpad script, before any full run):**
   - **Compare:** the old function (taken from `HEAD`) with the new one, for all 3,742 travelers.
   - **Networks:** car (`initial_network/auto_edges.csv`), FRT (`initial_network/initial_super_network_non_micro_hw_20.csv`),
     the initial microtransit network (`initial_network/initial_super_network_micro_hw_10_virstop_75.csv`) and the
     four per-period final networks (`final_network/final_super_network_micro_fsize_2_ophr_15_*_hw_10_virstop_75.csv`,
     present after any full run).
   - **Settings:** rejection penalty 0 and > 0, iteration 0 and > 0, with the fares of `input_parameter.csv`.
   - **Pass rule:** every returned dict must be equal, including key order, and so must `parking_dur` and `bt_c_gas`.
2. **Speed:** the same sample benchmark as above (every 10th traveler × 3 networks), old against new. Estimate: 2× or
   more for the function, which would bring the run from about 18 to about 9–11 minutes. Measuring will tell.
3. **Full seed-0 run:** `compare_reference.py` must print `REPRODUCED` (32 files), and `check_inputs.py` must pass.
4. **Docs:** a row and section in `docs/progress.md`, and a code-map note in the README if needed; set this plan's
   status to done.

## Decisions needed

1. **One step or two?**
   - **(a)** Do changes 1–5 in one step, verified as above. *(Recommended: the equivalence test checks all of it at
     once, and each full run takes about 20 minutes.)*
   - **(b)** Do change 1 alone first (with its own full run), then changes 2–5.
2. **Remove `get_link_type_from_O_to_D` once it is unused?** *(Recommended: yes. It is defined in
   `network_algorithms.py` and called only by this function.)*
3. **Add a guard?** It would stop the run with an error if a link cost is ever negative (for example, a negative
   coefficient in a future input), because the faster version relies on costs being ≥ 0. *(Recommended: yes; it
   doesn't change results.)*

User's answers (2026-11-10): "Go with your recommendations for all three": 1 (a), 2 yes, 3 yes.

## Result (2026-11-10)

- Done as planned, in one step. `get_link_type_from_O_to_D` removed; `Heap_Node` and the new `out_links(graph)`
  (the link lists, kept in `graph.graph["out_links"]`) are at module level; the guard raises a `ValueError` naming
  the link and the traveler. `network_algorithms.py` 596 -> 572 lines.
- Equivalence test (all 3,742 travelers × 14 cases: car at iteration 0 and 2; FRT with the base and the scenario
  fare; the initial and the four final microtransit networks, each with rejection penalty 0 / iteration 0 and
  2.5 / iteration 3): **52,388 calls, 0 differing** (every returned value equal, dicts also in key order). CPU time
  1,845 s -> 632 s (2.9×). The debug print appeared 1,351,111 times with the old and 1,225,450 times with the new
  function in these cases (the effect described above).
- Sample benchmark (every 10th traveler × 3 networks): 15.8 s -> 5.1 s (3.1×); heap pushes and pops unchanged
  (856,480 / 681,119); 13% of the pops were outdated entries, now skipped.
- Full seed-0 run: **6 min 58 s** (before: 17 min 53 s); `compare_reference.py` **32 identical, `REPRODUCED`**;
  `check_inputs.py` passes; no new pyflakes warnings (the remaining ones are in the untouched skim functions).
