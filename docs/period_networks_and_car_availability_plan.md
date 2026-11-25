# Period-specific networks and car availability: plan and decisions

Written 2026-11-24. Two model features the user asked for, built on `main` (where they fall back to today's behaviour,
since Lemon Grove's inputs have neither) and then taken to the branch `TRA_resubmission` by a fast-forward, where the
new Lemon Grove inputs from `TRA_input_data_prep` (SANDAG ABM3) use them. Each step ends with a full run that prints
`REPRODUCED`.

## The user's request (2026-11-24)

1. The model uses period-specific networks when they are available, otherwise one network for the whole day. This
   applies to the period-specific super-network and to FleetPy's network: FleetPy uses `network_dynamics.csv` and
   the period travel-time files when they are there, otherwise only `base/`.
2. The path finding respects `auto_available` when the demand has it: a traveler without a car cannot choose the car.
   Without the column every traveler has the car option.

On the branch, TRA's (ABM3) periods are followed: the periods and everything tied to them must be flexible enough
that only the period boundaries (parameter values) change there.

## Decisions (user, 2026-11-24)

1. **Periods as data, in the area file** (option (b), then (a) for where they live). New area parameters
   `time_periods`, `period_start_h`, `period_end_h`, `peak_periods` replace the model parameters `day_start_h`,
   `am_end_h`, `md_end_h`, `pm_end_h`, `day_end_h` and the four period names written in the code. Lemon Grove on
   `main`: `AM;MD;PM;EV`, start 5, ends `10;15;20;24`, peak `AM;PM` (as today). On the branch: `EA;AM;MD;PM;EV`,
   start 3, ends `6;9;15.5;19;27`. A departure belongs to the first period whose end is at or after it; before the
   start: the first period, after the last end: the last (as today). `operating_periods_scenarios` stays in the
   model file and must name periods of the area.
2. **Which networks can be per period:** the super-network with microtransit (file 3) and the car network (file 5).
   The FRT-only network (file 4) and the base-headway FRT network (file 9) stay one network for the whole day. (The
   FRT part of the microtransit super-network is the same in every period too; TRA writes it so, and consistency
   rule 6 already requires it.) A file is per period when `<name>_<P>.csv` exists for every period `P`, whole-day
   when only the file without suffix exists; anything else is a checker error.
3. **FleetPy:** when the area's FleetPy network folder has `network_dynamics.csv`, the run stages it and its
   travel-time folders and sets `nw_dynamic_f`; otherwise only `base/` (as today). Plus the pandas-2 fix in
   FleetPy's `NetworkBasic.load_tt_file` (`iteritems` -> `items`), recorded in `fleetpy/LOCAL_CHANGES.md`, and
   checker rules for the folders.
4. **`auto_available`:** an optional demand column (`True`/`False` or `1`/`0`); missing = every traveler has a car.
   A traveler without a car: transit with probability 1 (scenario and base case), no car path searched, the logsum
   of transit only; the random draw is still made (the draw sequence stays the same). The checker requires the car
   reachability only for travelers with a car.
5. **Outputs:** (a) the individual results get an `auto_available` column only when the demand has it, so `main`'s
   outputs stay byte-identical.
6. **`micro_only`** (no transit outside the operating periods) with a traveler without a car: the run stops with a
   message (`micro_only` is not supported for a new area anyway).
7. **The freeway-node fix (I-33) on `main` too**, as step 1. In a network with car-only roads
   (`TRA_input_data_prep`'s `--local-edges`) the freeway nodes keep their numbers but have no walk or microtransit
   links, so their microtransit twins are unused; the startup check required every twin to be used.
8. **Steps,** one commit each, each with a full run `REPRODUCED`: (1) freeway-node fix; (2) `auto_available`;
   (3) flexible periods; (4) per-period super-network and car network; (5) FleetPy travel-time folders; (6) docs.
   Then the branch is fast-forwarded and the real test runs there on TRA's data.

Git (user's question): implemented on `main`; `TRA_resubmission` has no commits of its own, so it is not recreated
but brought up to date with `git switch TRA_resubmission` and `git merge --ff-only main`.

## Done

Step 1 done 2026-11-24 (`docs/progress.md`, "Period networks and car availability, step 1").
Step 2 done 2026-11-24 (`docs/progress.md`, "Period networks and car availability, step 2").
Step 3 done 2026-11-24 (`docs/progress.md`, "Period networks and car availability, step 3").
Step 4 done 2026-11-24 (`docs/progress.md`, "Period networks and car availability, step 4").
Step 5 done 2026-11-24 (`docs/progress.md`, "Period networks and car availability, step 5").
Step 6 done 2026-11-24 (`docs/progress.md`, "Period networks and car availability, step 6"). The plan is complete
on `main`.

### Next (as of 2026-11-24)

- Bring the branch up to date: `git switch TRA_resubmission`, `git merge --ff-only main`.
- On the branch: the held decisions on moving TRA's new Lemon Grove inputs (`new_LG_data/`) into `mtsm_data/`
  (decision 4 there, which period's network for the whole day, is replaced by the period networks); the area's
  periods set to ABM3's (`EA;AM;MD;PM;EV`, 3, `6;9;15.5;19;27`); the first run on period data and its reference.
- Open items from this plan: I-35 (in progress), I-42, I-43.
