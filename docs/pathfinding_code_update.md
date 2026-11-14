# Path search (I-22): what was tried on 2026-11-14

Status: **tried and taken back. Nothing of it is in the code.** The user's decision (2026-11-14): not to implement it
now; I-22 stays open (`docs/open_issues.md`). This file records the trial, so that the work can be taken up again
without repeating it. After the code was restored, a full seed-0 run printed `32 identical, REPRODUCED`.

Function: `generalized_cost_dijsktra_OD_heap` in `mtsm_model/helpers/network_algorithms.py`. It finds a traveler's
least generalized cost path: by car (auto network), by walk + FRT (base case) and by walk + microtransit + FRT.

In short:

- The fix works: a search with one path per label finds a cheaper path for 405 of 3,472 travelers, as predicted.
- The reported totals move little.
- The correct search shows a loophole in the fare rules: very short microtransit rides bought only to make the FRT
  fare free. This is why the fix should be decided together with the fare rules (I-24).

## The issue

The search is a Dijkstra search over nodes: for every node it keeps one path, the cheapest found so far, and drops
every other path to that node. This is only right if the cost of a link does not depend on the path before it. In
this function three link costs do:

| Link | Its cost depends on | Rule |
|---|---|---|
| FRT boarding (type 2, walk node -> stop) | has the path used microtransit? | FRT fare x `micro2fixed_factor` |
| FRT boarding (type 2, walk node -> stop) | was the previous link an alighting? | boarding again at the same walk node: no FRT fare |
| Microtransit in-vehicle (type 4) | has the path used FRT? | distance fare x `fixed2micro_factor` |

With the transfer penalty on (`enable_num_transfer_penalty`, off in the reference; I-25) there are two more: a
boarding after a transit leg, and an FRT link after an FRT link of another route, each cost `bt_f_trfer`.

## The reason

Two paths can reach the same walk node:

- path A, by walking: cheaper so far;
- path B, with a microtransit ride: dearer so far, but with `micro2fixed_factor` 0 the FRT ride after it is free.

The search keeps A and drops B, also when B is cheaper at the destination. So the model's "least-cost" transit path
is sometimes not the least-cost one. The error grows with the transfer discount.

Example from the reference networks (traveler 1103, AM):

| | Generalized cost | Time | Fare | Path |
|---|---:|---:|---:|---|
| Search now | 12.351 | 1,261 s | 7.23 $ (FRT twice) | walk 405 s, FRT, walk 67 s, FRT |
| Label search | 11.652 | 1,289 s | 7.65 $ (microtransit; FRT free) | walk 186 s, microtransit 52 s, FRT, walk 67 s, FRT |

## The fix that was tried

The search keeps the least-cost path per **label**. A label is a node together with everything a later link cost
reads about the path so far:

    (node, used, route_pre)

- `used`: a sum of
  - `USED_MICRO` (1): the path has a microtransit in-vehicle link (type 4);
  - `USED_FRT` (2): the path has an FRT in-vehicle link (type 1);
  - `JUST_ALIGHTED` (4): the node is a walk node reached on an FRT waiting link. It holds for this node only.
- `route_pre`: the route of the FRT link the node was reached on. Kept only when the transfer penalty is on, `None`
  otherwise.

Two paths to the same node are compared only if they have the same label. A walk node has up to 6 labels. The first
label of the destination that leaves the heap is the least-cost path. The link costs were not touched. In the car
network no link cost depends on the path before, so a car path has one label per node.

The parts of the function that changed (the cost lines between them stay as they are):

```python
USED_MICRO, USED_FRT, JUST_ALIGHTED = 1, 2, 4

    start = (initial, 0, None)          # all dictionaries of the search are per label, not per node
    visited_temp = {start: bt_t_0}
    path = {}                           # {label: (previous label, link type, route)}
    ...
    while heap_q:
        min_label = heapq.heappop(heap_q).label
        if min_label in settled:
            continue
        settled.add(min_label)
        min_node, used, route_pre = min_label
        ...
        if min_node == dest:
            dest_label = min_label
            break
        if min_node in links:
            # what the link costs read about the path so far, from the label
            IsMicroLink, IsFixedLink = bool(used & USED_MICRO), bool(used & USED_FRT)
            if used & JUST_ALIGHTED:
                link_type_pre = 2
            elif route_pre is not None:
                link_type_pre = 1
            else:
                link_type_pre = 0
            used_on = used & (USED_MICRO | USED_FRT)
            for edge, link_travel_time, link_type_, link_length, route in links[min_node]:
                ...                     # the link costs, unchanged
                if link_type_ == 4:
                    label = (edge, used_on | USED_MICRO, None)
                elif link_type_ == 1:
                    label = (edge, used_on | USED_FRT, route if transfer_penalty_on else None)
                elif link_type_ == 2 and edge <= last_walk_node:  # alighting
                    label = (edge, used_on | JUST_ALIGHTED, None)
                else:
                    label = (edge, used_on, None)
                if label not in visited_temp or temp < visited_temp[label]:
                    visited_temp[label] = temp
                    path[label] = (min_label, link_type_, route)
                    heapq.heappush(heap_q, Heap_Node(label, temp))
                    ...                 # time, distance and fares of the label


def label_trajectory(origin, destination, dest_label, path, value_at):
    """[origin, (node, value at the node, link type into the node, route), ..., destination]"""
    rows = []
    label = dest_label
    while label in path:
        previous_label, link_type, route = path[label]
        rows.append((label[0], value_at[label], link_type, route))
        label = previous_label
    rows.append(origin)
    rows.reverse()
    rows.append(destination)
    return rows
```

Other changes that came with it:

- The trajectory has to be followed label by label (`label_trajectory` in place of `getTrajectory_O_to_D`), because a
  least-cost path can pass a node twice with different labels (18 paths did).
- The function returned only what the callers read: the six values at the destination as one-entry dicts
  `{destination: value}` and the time and distance trajectories. `choice.py` reads the values at the destination,
  `iteration.py` the trajectories; nothing else is read.
- `mtsm_model/paths.py`: took the trajectories from the search; `AutoPath` and `FrtPath` lost the fields `path` and
  `time_path`; `dest_only` was no longer needed. `mtsm_model/iteration.py`: stored the paths as returned.

## Checks of the label search

The search now (from git) and the label search, on the reference run's networks, for every traveler; rejection
penalty 0, as in the reference run (it had no rejections).

| Search | Travelers | Same result (values and both trajectories) | Label search cheaper | Dearer |
|---|---:|---:|---:|---:|
| Car | 3,742 | 3,742 | 0 | 0 |
| FRT-only network (base case) | 3,742 | 3,740 | 0 | 0 |
| With microtransit, AM to PM (final networks) | 3,472 | 3,063 | **405 (11.7 %)** | 0 |
| With microtransit, EV (no microtransit) | 270 | 270 | 0 | 0 |

- **405 travelers** get a cheaper path; path now -> label search: FRT -> microtransit + FRT 275, microtransit + FRT
  -> microtransit + FRT 56, walk -> microtransit + FRT 36, microtransit -> microtransit + FRT 35, FRT -> FRT 3.
  Saving in generalized cost: median 0.64, largest 5.76. These are the numbers of the independent exact search of
  2026-11-11 (405 and 275; I-22).
- **The cost of every new path was recomputed link by link** by separate code: no difference for any traveler.
- **Equal-cost paths:** 2 base-case travelers and 4 with microtransit got another path of exactly the same cost,
  time, distance and fare (route 936 between walk nodes 103 and 700 exists as two chains of stops with the same
  total time; the order of the heap decides).
- **The rejection penalty matters for the count:** with a penalty of 0.6 (rejection rate 20 % x 3 $) it is 169
  travelers, not 405.
- Other settings: with the transfer penalty on, 244 travelers with microtransit and 21 in the base case get a
  cheaper path; with both factors 0.5, 256 travelers (49 were logged on 2026-11-11; the difference was not traced).
  In all cases no path got dearer and the recomputed costs agreed.

## Results change (full seed-0 run with the label search against the reference)

`tools/compare_reference.py`: 13 identical, 19 differing. 6 iterations as before.

- **Base case (`FRT_only` column of the evaluation file): no value changed.**
- Differing: the evaluation file, the individual results, the transit link riders, the MD and PM accessibility files
  and final networks, FleetPy's demand, results and user statistics of all iterations.

Evaluation file, column `FRT_and_micro` (57 of its 73 values differed; the main ones):

| Metric | Reference | Label search |
|---|---:|---:|
| `car_users` | 3,444 | 3,442 |
| `trsit_mode_users (W_M_F)` | 298 | 300 |
| `walk_users` | 249 | 251 |
| `pure_F_users` | 15 | 14 |
| `M_pls_F_users` | 6 | 9 |
| `M_trips` | 68 | 71 |
| `F_trips` | 22 | 26 |
| `F_revenue ($)` | 65.08 | 57.85 |
| `M_revenue ($)` | 864.88 | 878.10 |
| `avg_F_fare` | 3.099 | 2.515 |
| `tot_sub ($)` | 7,781.65 | 7,776.56 |
| `tt_mob_lgsm_inc_with_micro` | 903.05 | 901.76 |
| `M_avg_wait_time (s)` | 209.4 | 210.5 |
| `wghted_acc_emp_15_min` | 6,331.68 | 6,329.49 |

Optimizer objectives of this parameter set: subsidy -5,460.99 -> -5,455.89; logsum increase 903.05 -> 901.76.

The totals move little although 405 paths change, because about 92 % of the travelers choose the car whatever the
transit path is.

**Not explained:** the logsum increase is lower with the label search (901.76 against 903.05), although it only
finds cheaper paths on the same network. FleetPy's waiting times in the final networks differed (209.4 -> 210.5 s),
but whether that accounts for it was not traced. To be traced before a new reference is made.

## Side finding: very short microtransit rides that make the FRT fare free

With `micro2fixed_factor` 0 (the reference value) any microtransit ride makes every later FRT boarding free. The
correct search uses this. Least-cost paths on the reference's final networks (AM to PM, 3,472 travelers):

| | Search now | Label search |
|---|---:|---:|
| Walk only | 1,597 | 1,561 |
| FRT | 1,075 | 800 |
| Microtransit | 629 | 594 |
| Microtransit + FRT | 171 | 517 |
| of these: shortest microtransit ride under 30 s | 1 | 211 |
| of these: shortest microtransit ride under 60 s | 14 | 284 |

Example (traveler 6776, MD): a microtransit ride of 1 s for 2.40 $, then two free FRT rides; cost 9.008 against
14.737 for the path now (one FRT ride for 3.62 $ and a walk of 25 min).

Why the model takes such a ride (traveler 6776, in the model's cost units):

| Item | Cost |
|---|---:|
| Microtransit wait of 208 s (`bt_m_wt` 0.16 per minute) | 0.55 |
| Microtransit fare 2.40 $ (`bt_t_fr` 1.457 per $) | 3.50 |
| The ride in all | 4.05 |
| One FRT fare of 3.62 $ saved | 5.27 |

- The discount is total (factor 0).
- Off-peak the start fare (2.38 $) is below the FRT fare (3.62 $); in the peaks it is about 5.64 $ (x 2.37).
- The discount needs only one microtransit link, and two road nodes can be 1 s apart.
- Only the waiting time counts against the ride. For the median traveler (`bt_m_wt` 0.15, `bt_t_fr` 0.685) the ride
  costs about 2.15 off-peak and one free boarding saves 2.48.

This is the least-cost path under the present fare rules, not an error of the search: a loophole of the rules as
coded (I-24), which the search now mostly hides. Such rides would also put requests of a few metres into FleetPy.

Noticed in the demand file, not checked: `bt_t_fr` ranges from 0.05 to 233.5 (median 0.685).

## Trial of a fare rule: the discount for the next FRT boarding only

Tried in a copy of the label search outside the repository: a microtransit ride gives the factor
`micro2fixed_factor` to the next FRT boarding only; a later boarding pays what it pays without microtransit (the
full fare, or nothing right after an alighting at the same walk node). One more item in the label (`DISCOUNT_READY`:
set by a microtransit link, cleared by an FRT boarding).

Path search on the reference's final networks (AM to PM, 3,472 travelers):

| Least-cost paths | Discount for the whole trip | Next FRT boarding only |
|---|---:|---:|
| Walk only | 1,561 | 1,566 |
| FRT | 800 | 848 |
| Microtransit | 594 | 606 |
| Microtransit + FRT | 517 | 452 |
| of these: shortest microtransit ride under 30 s | 211 | 163 |
| of these: shortest microtransit ride under 60 s | 284 | 221 |

Of the 163 rides under 30 s, 161 are in MD and 2 in the peaks (whole trip: 169 MD, 42 peak). 130 travelers get a
dearer least-cost path than with the whole-trip rule, none a cheaper one. The rule limits the short rides; it does
not stop them.

Full seed-0 run, evaluation file, column `FRT_and_micro` (the base case is the same in all three):

| Metric | Reference | Label search, whole trip | Label search, next boarding only |
|---|---:|---:|---:|
| `car_users` | 3,444 | 3,442 | 3,444 |
| `M_trips` | 68 | 71 | 68 |
| `F_trips` | 22 | 26 | 22 |
| `M_pls_F_users` | 6 | 9 | 6 |
| `F_revenue ($)` | 65.08 | 57.85 | 65.08 |
| `M_revenue ($)` | 864.88 | 878.10 | 863.89 |
| `tot_sub ($)` | 7,781.65 | 7,776.56 | 7,782.64 |
| `tt_mob_lgsm_inc_with_micro` | 903.05 | 901.76 | 905.24 |
| `M_avg_wait_time (s)` | 209.39 | 210.46 | 209.39 |

With this rule the travelers' choices (all user and trip counts, the car miles, FleetPy's vehicle miles and waiting
time) were those of the reference; 17 of 32 files were identical to it.

Rules that would close the loophole, not tried: a smallest microtransit ride for the discount; a floor, so that
microtransit + FRT never costs less than the FRT fare alone. A factor above 0 makes it smaller.

## Run time

The label search does more work: 1.4 times the time on the FRT-only network, 1.8 times on the network with
microtransit (about 1,480 labels leave the heap per search; the network has 2,269 nodes); the car search is
unchanged. Full run: 9 min 50 s (whole trip) and 10 min 39 s (next boarding only), against 6 to 7 min now. Not
tried: dropping labels that cannot win.

## When this is taken up again

1. Decide the fare rules first (I-24, the loophole above), so that the reference changes once.
2. Put the label search back (section "The fix that was tried"), with the label items the chosen rules need.
3. Repeat the checks: car paths identical; no path dearer than now; the cost of every path recomputed by separate
   code; with the rules of today, 405 travelers cheaper on the reference networks.
4. Trace the lower logsum before accepting the numbers.
5. Full run, comparison with the reference, new reference with a note in `docs/reference_results/README.md`, second
   run `REPRODUCED`. Earlier optimizer sessions are then not comparable.

## Log

- 2026-11-14: label search written and checked; full run compared with the reference; fare-rule trial in a copy;
  user's decision not to implement it now; code restored (`git status` clean, full run `REPRODUCED`); this file
  written.
