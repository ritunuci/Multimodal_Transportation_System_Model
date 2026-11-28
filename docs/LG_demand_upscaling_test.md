# Lemon Grove: testing `demand_upscaling` on 10 % and 25 % samples (2026-11-27)

Branch `TRA_resubmission`, TRA's new Lemon Grove inputs (`docs/new_lemon_grove_data_move.md`). The question: when
the model runs on a sample of the travelers with `demand_upscaling` on, how close do its results come to a run on
all travelers? A sample run is much faster, so the optimizer could use one, but only if its results scale up well.
Summary in `docs/progress.md` ("`demand_upscaling` on 10 % and 25 % samples against the full run"). How the switch
works: `docs/open_issues.md`, I-32 (update 2026-11-25) and I-45.

## 1. Result in short

- **Run time:** the 25 % sample takes 17 min 30 s against the full run's 1 h 00 min 48 s (3.5 x faster); the 10 %
  sample takes 8 min 25 s (7.2 x faster).
- **Close to the full run (25 %):** car and transit users (within 0.6 %), total subsidy (-0.3 %), microtransit
  passenger miles (-1.9 %), FRT trips (-2.7 %), microtransit operating cost (-0.7 %), car VMT (0.0 %).
- **Off by several percent:** microtransit trips (-8.4 %), the logsum increase (+8.0 %), the microtransit wait
  (-5.4 %).
- **Biased in both samples:** the fleet's miles are too low (-20.4 % at 25 %, -29.7 % at 10 %), its occupancy too
  high and its utilisation too low; mode switches are 15 % low.
- **10 % is noisier** than 25 % on almost every value (FRT trips +19.5 %, microtransit wait +15.8 %, subsidy
  -5.5 %).
- Causes found (section 7): the synthetic FleetPy requests cluster around their sample request, so FleetPy pools them
  more than real requests; and each traveler's random draw differs between a sample run and the full run. The
  shortfall in mode switches is not explained yet.

## 2. Sample files

The user made both files and put them in `mtsm_data/lemon_grove/demand/` (committed 2026-11-27, `8d00449`). MTSM
does not draw samples itself (I-32). Checked before the runs (scripts in the session scratchpad, not in the
repository):

| | `demand.csv` (full) | `demand_10pct.csv` | `demand_25pct.csv` |
|---|---|---|---|
| Rows | 42,698 | 4,270 (10.00 %) | 10,674 (25.00 %) |
| In the model's day (5:00-24:00) | 42,380 | 4,240 | 10,603 |
| Scaled up | | x 10 = 42,400 | x 4 = 42,412 |
| Rows byte-identical to a row of `demand.csv` | | all | all |
| Unique `request_id` | yes | yes | yes |
| Header, line endings | CRLF | as full | as full |

- The 10 % sample's travelers are all in the 25 % sample.
- Shares against the full file (sample / full): periods EA 0.004 / 0.004, AM 0.240 / 0.240 (25 %: 0.242), MD
  0.406 / 0.409 (25 %: 0.415), PM 0.266 / 0.260 (25 %: 0.255), EV 0.084 / 0.087; trip modes, `auto_available` and
  trip purposes within about 0.5 percentage points.
- `tools/check_study_area.py` with each run's model file: 0 errors, 0 warnings, 1 note (trips outside the model's
  day: 30 for 10 %, 71 for 25 %).
- Not in the area manifest: `tools/check_inputs.py` lists only `demand/demand.csv` as the demand file (file 2), so
  it does not check the sample files.

## 3. Runs

All three runs use the same code and inputs except the demand settings: fleet size 7, transfer penalty on, seed 0,
microtransit `AM;MD;PM`, FRT headway 10 min (base case 20), virtual stops 75 %. The code is that of commit `98a6c6b`
(the later commits change only docs and add the sample files).

| | Full demand | 25 % sample | 10 % sample |
|---|---|---|---|
| Date | 2026-11-26 | 2026-11-27 | 2026-11-27 |
| `demand_upscaling` | False | True | True |
| `demand_sample_share` | 1 | 0.25 | 0.1 |
| `sample_demand_file` | none | `demand/demand_25pct.csv` | `demand/demand_10pct.csv` |
| Model file | frozen file | a copy, passed with `--config` | a copy, passed with `--config` |
| Results scaled by | 1 | 4 | 10 |

The two sample runs used copies of `mtsm_data/input_parameter/mtsm_constant_configurations.csv` with only those
three lines changed, passed with `run_examples_new_parking.py --config`; the frozen file still has
`demand_upscaling` False. To repeat a sample run: make such a copy and run
`python run_examples_new_parking.py --config <copy>`.

## 4. Run times

The model's own timer (`total run time is:` at the end of the run log); measured from outside, each run takes 7-9 s
more (Python starting and the run relaunching itself with a fixed hash seed).

| | Full demand | 25 % sample | 10 % sample |
|---|---|---|---|
| Start | 2026-11-26 17:38:02 | 2026-11-27 08:33:25 | 2026-11-27 08:24:53 |
| Total run time | **1:00:48** | **0:17:30** | **0:08:25** |
| Measured from outside | 1:00:55 | 0:17:37 | 0:08:34 |
| Iterations (then the base case) | 8 (0-7) | 8 (0-7) | 7 (0-6) |
| Per iteration, about | 7.6 min | 2.2 min | 1.2 min |
| Faster than the full run | 1 x | 3.5 x | 7.2 x |
| 50 optimizer candidates, about | 50 h | 15 h | 7 h |

FleetPy's share is 0.5-1.2 min per iteration in every run, since it serves about the same number of requests (section
5); the rest is MTSM's path search and choice model, which grows with the number of travelers.

Convergence (iteration, sum of squared percentage differences):

- Full: (1, 207.9), (2, 66.2), (3, 4.65), (4, 0.54), (5, 0.16), (6, 0.0), (7, 0.0).
- 25 %: (1, 50.2), (2, 10.5), (3, 0.15), (4, 0.15), (5, 0.037), (6, 0.00002), (7, 0.0).
- 10 %: (1, 20.3), (2, 0.68), (3, 0.042), (4, 0.030), (5, 0.0017), (6, 0.0).

## 5. FleetPy's requests

With `demand_upscaling` on, FleetPy gets the sample's microtransit requests plus round(n x (1 / share - 1))
synthetic ones: copies of the sample's requests, shifted in time by up to +-15 min within the period, with origin
and destination each a virtual stop within 400 m walking distance (`synthetic_time_shift_min`,
`synthetic_stop_radius_m`; I-45).

| | Full demand | 25 % sample | 10 % sample |
|---|---|---|---|
| Iteration 0 | 824 | 195 + 585 = 780 | 82 + 738 = 820 |
| Later iterations | about 500 (last: 502) | 115 + 345 = 460 | 50 + 450 = 500 |
| Last iteration, AM / MD / PM / EV | 80 / 315 / 101 / 4 | 81 / 258 / 120 / 0 | 90 / 300 / 110 / 0 |
| Rejected, last iteration | 0 | 0 | 9 (in MD) |
| FleetPy's simulation end | 68,640 s | 68,400 s | 68,400 s |

The number of requests comes out right within sampling noise; how they are spread over space and time is what
differs (section 7, finding 2). No request of the sample runs fell after 19:00, so the warning "MICRO USER OUTSIDE
THE OPERATING PERIODS DETECTED" of the full run (I-46) did not appear there.

## 6. Results against the full run

From each run's `output/lemon_grove_evaluation.csv`. With `demand_upscaling` on, the run itself scales the sums over
the sample's travelers by 1 / share (counts, revenues, costs of travel, miles, the logsum increase, mode switches);
the FRT schedule's cost and miles and FleetPy's values are not scaled (they already describe all travelers), and
shares and averages are ratios of scaled sums (I-32). Differences are (sample - full) / full. Shares (%) are
fractions, as in the evaluation file.

### 6.1 Base case (FRT only)

The base case has no microtransit, so FleetPy plays no part: its differences show the sampling noise alone (with
the different random draws, finding 1).

| Metric | Full | 10 % | 25 % | 10 % vs full | 25 % vs full |
|---|---|---|---|---|---|
| tt_agents | 42,380.0 | 42,400.0 | 42,412.0 | +0.0 % | +0.1 % |
| car_users | 35,596.0 | 35,640.0 | 35,596.0 | +0.1 % | +0.0 % |
| car_mode_share (%) | 0.840 | 0.841 | 0.839 | +0.1 % | -0.1 % |
| trsit_mode_users (W_M_F) | 6,784.0 | 6,760.0 | 6,816.0 | -0.4 % | +0.5 % |
| pure_walk_users | 6,396.0 | 6,330.0 | 6,392.0 | -1.0 % | -0.1 % |
| pure_M_users | 0.000 | 0.000 | 0.000 | - | - |
| M_trips | 0.000 | 0.000 | 0.000 | - | - |
| pure_F_users | 388.0 | 430.0 | 424.0 | +10.8 % | +9.3 % |
| F_trips | 406.0 | 450.0 | 440.0 | +10.8 % | +8.4 % |
| M_pls_F_users | 0.000 | 0.000 | 0.000 | - | - |
| tt_mode_switch | 0.000 | 0.000 | 0.000 | - | - |
| M_oper_cost ($) | 0.000 | 0.000 | 0.000 | - | - |
| F_oper_cost ($) | 2,352.0 | 2,352.0 | 2,352.0 | +0.0 % | +0.0 % |
| M_revenue ($) | 0.000 | 0.000 | 0.000 | - | - |
| F_revenue ($) | 1,015.0 | 1,125.0 | 1,100.0 | +10.8 % | +8.4 % |
| tot_sub ($) | 1,337.0 | 1,227.0 | 1,252.0 | -8.2 % | -6.4 % |
| sub_per_M_trip ($) | 0.000 | 0.000 | 0.000 | - | - |
| sub_per_T_trip ($) | 3.293 | 2.727 | 2.846 | -17.2 % | -13.6 % |
| tt_mob_lgsm_inc_with_micro | 0.000 | 0.000 | 0.000 | - | - |
| M_avg_wait_time (s) | 0.000 | 0.000 | 0.000 | - | - |
| F_avg_wait_time (s) | 573.4 | 573.3 | 578.2 | -0.0 % | +0.8 % |
| fleetpy_wait | 0.000 | 0.000 | 0.000 | - | - |
| rejection_rate | 0.000 | 0.000 | 0.000 | - | - |
| M_VMT (mi) | 0.000 | 0.000 | 0.000 | - | - |
| M_PMT (mi) | 0.000 | 0.000 | 0.000 | - | - |
| M_util_rate (%) | 0.000 | 0.000 | 0.000 | - | - |
| M_veh_occ | 0.000 | 0.000 | 0.000 | - | - |
| F_PMT (mi) | 622.9 | 705.7 | 639.0 | +13.3 % | +2.6 % |
| car_VMT (mi) | 36,381.2 | 36,153.7 | 36,319.1 | -0.6 % | -0.2 % |
| tt_VMT (mi) | 38,003.1 | 37,775.6 | 37,941.1 | -0.6 % | -0.2 % |
| tt_o_pckt_cost ($) | 15,652.5 | 15,670.9 | 15,712.5 | +0.1 % | +0.4 % |
| tt_gen_cost | 47,990.1 | 48,070.6 | 48,214.2 | +0.2 % | +0.5 % |

### 6.2 Scenario (FRT + microtransit)

| Metric | Full | 10 % | 25 % | 10 % vs full | 25 % vs full |
|---|---|---|---|---|---|
| tt_agents | 42,380.0 | 42,400.0 | 42,412.0 | +0.0 % | +0.1 % |
| car_users | 35,223.0 | 35,310.0 | 35,300.0 | +0.2 % | +0.2 % |
| car_mode_share (%) | 0.831 | 0.833 | 0.832 | +0.2 % | +0.1 % |
| trsit_mode_users (W_M_F) | 7,157.0 | 7,090.0 | 7,112.0 | -0.9 % | -0.6 % |
| pure_walk_users | 6,203.0 | 6,060.0 | 6,220.0 | -2.3 % | +0.3 % |
| pure_M_users | 493.0 | 480.0 | 448.0 | -2.6 % | -9.1 % |
| M_trips | 502.0 | 500.0 | 460.0 | -0.4 % | -8.4 % |
| pure_F_users | 452.0 | 530.0 | 432.0 | +17.3 % | -4.4 % |
| F_trips | 477.0 | 570.0 | 464.0 | +19.5 % | -2.7 % |
| M_pls_F_users | 9.000 | 20.000 | 12.000 | +122.2 % | +33.3 % |
| tt_mode_switch | 625.0 | 530.0 | 528.0 | -15.2 % | -15.5 % |
| M_oper_cost ($) | 12,249.7 | 12,124.9 | 12,164.2 | -1.0 % | -0.7 % |
| F_oper_cost ($) | 4,704.0 | 4,704.0 | 4,704.0 | +0.0 % | +0.0 % |
| M_revenue ($) | 5,329.7 | 5,456.7 | 5,342.2 | +2.4 % | +0.2 % |
| F_revenue ($) | 1,699.2 | 1,988.5 | 1,634.2 | +17.0 % | -3.8 % |
| tot_sub ($) | 9,924.9 | 9,383.8 | 9,891.8 | -5.5 % | -0.3 % |
| sub_per_M_trip ($) | 13.785 | 13.336 | 14.830 | -3.3 % | +7.6 % |
| sub_per_T_trip ($) | 10.138 | 8.770 | 10.705 | -13.5 % | +5.6 % |
| tt_mob_lgsm_inc_with_micro | 7,142.7 | 6,605.6 | 7,714.7 | -7.5 % | +8.0 % |
| M_avg_wait_time (s) | 386.1 | 446.9 | 365.3 | +15.8 % | -5.4 % |
| F_avg_wait_time (s) | 289.9 | 289.5 | 287.1 | -0.2 % | -1.0 % |
| fleetpy_wait | 433.9 | 498.6 | 418.2 | +14.9 % | -3.6 % |
| rejection_rate | 0.000 | 0.018 | 0.000 | n/a | - |
| M_VMT (mi) | 763.1 | 536.1 | 607.6 | -29.7 % | -20.4 % |
| M_PMT (mi) | 453.9 | 449.7 | 445.5 | -0.9 % | -1.9 % |
| M_util_rate (%) | 51.780 | 38.575 | 43.782 | -25.5 % | -15.4 % |
| M_veh_occ | 0.565 | 0.826 | 0.732 | +46.1 % | +29.5 % |
| F_PMT (mi) | 706.2 | 818.6 | 691.0 | +15.9 % | -2.2 % |
| car_VMT (mi) | 35,929.3 | 35,761.2 | 35,925.6 | -0.5 % | -0.0 % |
| tt_VMT (mi) | 39,936.3 | 39,541.3 | 39,777.1 | -1.0 % | -0.4 % |
| tt_o_pckt_cost ($) | 21,484.5 | 21,833.2 | 21,430.5 | +1.6 % | -0.3 % |
| tt_gen_cost | 48,518.1 | 48,385.6 | 48,688.7 | -0.3 % | +0.4 % |

### 6.3 Sampling alone

To tell the error of sampling from the error of the upscaling method, the full run's own individual results
(`individual_results_*_M_fsize_7_op_hr_13_hw_10_virstop_75.csv`) were taken for just the sample's travelers and
scaled by 1 / share. That is what a perfect upscaling would give for these travelers. "Sampling only" compares it
with the full run; the last column compares the sample run itself. "M users" and "F users" are travelers with any
microtransit or FRT distance (so microtransit + FRT users count in both); "logsum inc" is the sum of
`mob_logsum_increased_with_micro`.

Scenario, 10 % sample:

| value | full run | full run, sample's travelers x 10 | 10% run x 10 | sampling only | 10% run vs full |
|---|---|---|---|---|---|
| travelers | 42,380.0 | 42,400.0 | 42,400.0 | +0.0 % | +0.0 % |
| car | 35,223.0 | 35,500.0 | 35,310.0 | +0.8 % | +0.2 % |
| transit | 7,157.0 | 6,900.0 | 7,090.0 | -3.6 % | -0.9 % |
| M users | 502.0 | 500.0 | 500.0 | -0.4 % | -0.4 % |
| F users | 462.0 | 470.0 | 550.0 | +1.7 % | +19.0 % |
| M PMT | 453.9 | 425.0 | 449.7 | -6.4 % | -0.9 % |
| logsum inc | 7,142.7 | 7,772.4 | 6,605.6 | +8.8 % | -7.5 % |
| switches | 625.0 | 570.0 | 530.0 | -8.8 % | -15.2 % |

Scenario, 25 % sample:

| value | full run | full run, sample's travelers x 4 | 25% run x 4 | sampling only | 25% run vs full |
|---|---|---|---|---|---|
| travelers | 42,380.0 | 42,412.0 | 42,412.0 | +0.1 % | +0.1 % |
| car | 35,223.0 | 35,264.0 | 35,300.0 | +0.1 % | +0.2 % |
| transit | 7,157.0 | 7,148.0 | 7,112.0 | -0.1 % | -0.6 % |
| M users | 502.0 | 504.0 | 460.0 | +0.4 % | -8.4 % |
| F users | 462.0 | 472.0 | 448.0 | +2.2 % | -3.0 % |
| M PMT | 453.9 | 433.1 | 445.5 | -4.6 % | -1.9 % |
| logsum inc | 7,142.7 | 7,427.0 | 7,714.7 | +4.0 % | +8.0 % |
| switches | 625.0 | 604.0 | 528.0 | -3.4 % | -15.5 % |

Base case (car, transit, FRT users, walk only):

| Value | Full run | 10 %: sampling only | 10 %: sample run | 25 %: sampling only | 25 %: sample run |
|---|---|---|---|---|---|
| car | 35,596 | 35,850 (+0.7 %) | 35,640 (+0.1 %) | 35,608 (+0.0 %) | 35,596 (+0.0 %) |
| transit | 6,784 | 6,550 (-3.4 %) | 6,760 (-0.4 %) | 6,804 (+0.3 %) | 6,816 (+0.5 %) |
| F users | 388 | 440 (+13.4 %) | 430 (+10.8 %) | 412 (+6.2 %) | 424 (+9.3 %) |
| walk only | 6,396 | 6,110 (-4.5 %) | 6,330 (-1.0 %) | 6,392 (-0.1 %) | 6,392 (-0.1 %) |

The same travelers' choices in the scenario, sample run against full run:

- 10 %: same car/transit choice as in the full run: 3449/4240; same microtransit use: 4168/4240
- 25 %: same car/transit choice as in the full run: 8564/10603; same microtransit use: 10424/10603

## 7. Findings

1. **A traveler's random draw differs between a sample run and the full run.** The choice model draws one random
   number per traveler from a single stream, in the order of the travelers (`iteration.py`, `random.random()`), so
   leaving travelers out shifts every later draw. Checked: 0 of 4,240 and 0 of 10,603 travelers have the same draw
   (`agent_ran_num`) as in the full run, although their choice probabilities in the base case are identical (all
   4,240 and 10,603). So only totals are comparable, not individual choices (81 % of the travelers make the same car
   or transit choice), and the totals carry extra noise. For small groups this noise is large: about 400 FRT riders
   in the base case come out 8-11 % high in both samples.
2. **The fleet's miles are underestimated and its occupancy overestimated.** FleetPy gets about the right number of
   requests (460 and 500 against 502), but each synthetic request is a copy of a sample request within +-15 min
   and 400 m. Each sample request so becomes a cluster of 1 / share near-identical requests (4 at 25 %, 10 at 10 %),
   which FleetPy pools more easily than independent requests: microtransit VMT -20.4 % (25 %) and -29.7 % (10 %),
   occupancy 0.73 and 0.83 against 0.57, utilisation 43.8 % and 38.6 % against 51.8 %. The smaller the sample, the
   larger the clusters and the bias. The passenger miles, from MTSM's travelers, are close (-1.9 % and -0.9 %), and
   the microtransit operating cost moves little (-0.7 % and -1.0 %), since it is mostly per vehicle-hour.
3. **Mode switches are 15 % low in both samples** (528 and 530 against 625), more than sampling alone gives (-3.4 %
   and -8.8 %). Not explained yet; to look into.
4. **The logsum increase is off by about +-8 %** (25 %: +8.0 %, 10 %: -7.5 %). Sampling alone gives +4.0 % (25 %)
   and +8.8 % (10 %): of the same size, though for 10 % not of the same sign as the run, so the total carries
   noise of about +-8 % from the sample and the random draws together (finding 1); a few travelers with large
   logsum gains decide it.
5. **The total subsidy is close at 25 %** (-0.3 %; 10 %: -5.5 %), helped by the fixed FRT and fleet costs, which do
   not depend on the sample.

## 8. Options (decision needed)

- (a) Use the 25 % sample for the optimizer as it is: the subsidy, mode shares and operating cost are close; the
  logsum carries about +-8 % noise; fleet miles, utilisation and occupancy should not be reported from a sample run.
- (b) Reopen I-45 and make the synthetic requests cluster less (e.g. origin, destination and time drawn from
  different sample requests of the same period), then repeat the 25 % test.
- (c) Give each traveler a random draw fixed by its id (e.g. seeded by the run's seed and `request_id`), so a sample
  run and the full run agree traveler by traveler. It changes results, so it goes with the branch's new reference.
- (d) Run the optimizer on the full demand (about 1 h per candidate).

Recommended: (a) for now; (b) before the paper reports fleet values from sample runs; look into finding 3. The 10 %
sample is too noisy.

Opened as items in `docs/open_issues.md` (2026-11-27, user's request): finding 2 and the choice above as I-49,
finding 3 as I-50, finding 1 and option (c) as I-51.

## 8a. Re-run with a new copy rule (I-49, 2026-11-27 afternoon)

User's decision (b) of I-49 (`docs/open_issues.md`): a copy's time is the time of a sample request of the same
period (+-15 min), its stops within 800 m (was: the request's own time +-15 min, stops within 400 m). The 25 % sample
was run again (`demand_upscaling` True, share 0.25; total run time 0:17:55; 8 iterations). The code also has the
I-46/I-47 fix, which the runs above do not have (see the note below the table).

| Scenario, against the full run | 25 % above | 25 % with the new rule |
|---|---|---|
| FleetPy requests with a near twin (15 min, 400 m at both ends; full run 6.8 %) | 88.7 % | 7.5 % |
| Microtransit VMT | -20.4 % | +2.8 % |
| Utilisation | -15.4 % | +4.0 % |
| Occupancy | +29.5 % | +7.6 % |
| Microtransit wait (MTSM) | -5.4 % | +12.6 % |
| FleetPy wait | -3.6 % | +11.2 % |
| Rejection rate (full run 0) | 0 | 1.3 % |
| Microtransit trips | -8.4 % | -6.8 % |
| Car / transit users | +0.2 / -0.6 % | +0.2 / -0.5 % |
| `tot_sub` | -0.3 % | +1.5 % |
| Logsum increase | +8.0 % | -5.2 % |
| Mode switches | -15.5 % | -15.5 % |

Clustering is gone and the fleet values are close to the full run. Part of the higher VMT and wait comes from the
I-46 fix (requests start at the boarding stop: the sample's own requests 1.46 -> 1.57 km direct; the copies are
4-5 % longer than their request before and after the change), so a full run with the same code is needed for a
clean comparison. Mode switches and the logsum are as noisy as before (I-50, I-51).

## 8b. Against a full run of the same code (2026-11-27 evening)

The full demand was run again with the current code (I-46/I-47 fix in; `demand_upscaling` off; total run time
1:00:04), so the 25 % run of section 8a can be compared without the I-46 effect.

| Scenario | Full run, current code | 25 % run, I-49 rule | 25 % vs full |
|---|---|---|---|
| FleetPy requests with a near twin | 7.8 % | 7.5 % | |
| FleetPy requests (served) | 512 (505) | 468 (462) | -8.6 % |
| Mean direct distance of FleetPy's requests | 1.48 km | 1.63 km | +10 % |
| Microtransit VMT | 810.1 mi | 784.7 mi | -3.1 % |
| Utilisation | 55.3 % | 53.8 % | -2.6 % |
| Occupancy | 0.584 | 0.608 | +4.1 % |
| Microtransit wait (MTSM) | 400.3 s | 434.6 s | +8.6 % |
| Rejection rate | 1.4 % | 1.3 % | |
| Microtransit passenger miles | 462.6 | 449.8 | -2.8 % |
| Car / transit users | 35,216 / 7,164 | 35,288 / 7,124 | +0.2 / -0.6 % |
| `tot_sub` | 9,993.4 $ | 10,078.1 $ | +0.8 % |
| Logsum increase | 7,031.4 | 6,773.7 | -3.7 % |
| Mode switches | 625 | 528 | -15.5 % |

Fleet values are now within -3 to +4 % of the full run, the subsidy within 1 %, and the rejection rate the same.
The microtransit wait is 8.6 % high: the 25 % sample's own requests are longer than the full demand's (1.57 against
1.48 km), and the copies are 4 % longer than their request. Mode switches stay 15.5 % low (I-50).

The current full run against the full run of 2026-11-26 (the I-46/I-47 fix alone; I-49 does not act with
`demand_upscaling` off): microtransit VMT +6.2 % (763.1 -> 810.1 mi), utilisation +6.8 %, microtransit trips +2.0 %
(502 -> 512), wait +3.7 % (386.1 -> 400.3 s), rejection rate 0 -> 1.4 %, `tot_sub` +0.7 %; car and transit users
and the FRT values within 0.1 %; mode switches 625 both.

## 9. Where the outputs are

Local only (ignored by `mtsm_data/*/output/*`, so not in git); each folder holds the run's outputs in the layout of
`docs/reference_results/` (`output/`, `intermediate/...`) and its run log `run.log`. The full and 10 % copies are
to be deleted once the comparison is done (user's request 2026-11-26); the 25 % copy is kept as a backup (user's
decision 2026-11-27) and also holds the model file it ran with (`mtsm_config_sample_25pct.csv`).

| Run | Folder (in `mtsm_data/lemon_grove/output/`) | Files |
|---|---|---|
| Full demand | `full_demand_fsize7_2026-11-26/` | 36 |
| 25 % sample (kept) | `sample_25pct_2026-11-27/` | 37 (with its model file) |
| 25 % sample, I-49's new rule (section 8a) | `i49_25pct_2026-11-27/` | 37 (with its model file) |
| Full demand, current code (section 8b) | `full_demand_current_2026-11-27/` | 36 |
| 10 % sample | `sample_10pct_2026-11-27/` | 35 (7 iterations, so one `iter_*_user-stats.csv` fewer) |

The comparison scripts (evaluation tables, sampling alone, random draws) were run from the session scratchpad and
are not in the repository.
