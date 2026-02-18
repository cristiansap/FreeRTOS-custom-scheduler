# Test Suite

This document describes every test setup (each folder in `testing/`) and the specific scheduling scenario it checks. The goal is to make explicit what each test is intended to validate about the timeline-driven scheduler (HRT/SRT): start/end behavior, deadline enforcement, preemption, restarts, HRT/SRT behaviour and stress cases.

## How to run a test

Build + run a test:

```sh
make run TEST=XX
```

For verbose trace output + **GANTT chart**:

```sh
make trace TEST=XX
```

- **NOTE #1**: To run a test, simply write the two-digit number (XX) representing the test itself; it is not necessary to write the full name of the test subfolder.
- **NOTE #2**: A useful check after start is to look at the `vPrintSubframes()` output printed at startup — it shows the major/subframe layout and task placements. Deadline misses are reported through the scheduler trace hooks. Then the GANTT chart will automatically appear to confirm that the scheduler is working correctly.

## Legend

- HRT = Hard Real-Time task (has subframe, start, end). If it exceeds end, scheduler terminates it.
- SRT = Soft Real-Time task (executes in leftover/idle time inside subframe).
- The tests are named by directory; each `setup.c` in the directory builds the scenario and includes a short top comment describing intent.

## Tests

### T00-idle
- Purpose: sanity / bootstrap test.
- Scenario: no tasks are created; verifies scheduler initialization with empty workload.
- What to verify: scheduler starts and `vPrintSubframes()` prints an empty major/subframe layout (no tasks assigned).

### T01-hrt_single-4x10
- Purpose: minimal HRT case.
- Scenario: a small set of HRT tasks assigned to different subframes with non-overlapping start/end windows.
- What to verify: each HRT starts and ends according to configured times.

### T02-hrt_deadline_miss-4x10
- Purpose: deadline-miss enforcement.
- Scenario: HRT tasks use the infinite-work simulation function to force overruns and trigger deadline-miss handling.
- What to verify: scheduler detects deadline misses and forces termination of overrunning HRT tasks; trace shows proper deadline-miss handling.

### T03-hrt_neighboring-4x10
- Purpose: boundary and handoff correctness.
- Scenario: HRT entries are arranged to test exact boundaries and contiguous windows across subframes (including multiple HRTs per subframe in some cases).
- What to verify: no overlaps across boundaries, correct handoff and restart between adjacent subframes.

### T04-hrt_short-4x10
- Purpose: short-deadline verification.
- Scenario: HRT tasks with very short start/end intervals to stress deadline enforcement.
- What to verify: correct termination or completion depending on simulated work; ensure the scheduler flags deadline misses when execution cannot finish in the small window.

### T05-hrt_long-4x10
- Purpose: tasks occupying most of the subframe.
- Scenario: HRTs are sized to occupy (almost) the full subframe duration.
- What to verify: HRT scheduling remains consistent when windows are large and a single HRT occupies (almost) the entire subframe.

### T06-hrt_packed-4x10
- Purpose: tightly-packed HRTs inside subframes.
- Scenario: multiple HRTs placed serially inside the same subframe to validate scheduling multiple HRTs back-to-back.
- What to verify: order preservation, no deadline violation when each HRT fits its allocated slot, and correct termination when overruns occur.

### T07-srt_only-4x10
- Purpose: SRT-only behavior.
- Scenario: only SRT tasks are created (no HRTs) to observe best-effort scheduling.
- What to verify: SRT tasks run during idle time according to the fixed compile-time ordering; confirm correct SRT scheduling across subframes.

### T08-srt_overflow-2x5
- Purpose: SRT capacity overflow.
- Scenario: many SRT tasks scheduled into a small subframe so there is not time to run them all.
- What to verify: observe which SRTs execute and which are starved within the subframe; validate system remains stable under SRT overload.

### T09-srt_blocking-2x10
- Purpose: interaction of blocking/long HRTs with SRTs.
- Scenario: HRT tasks occupy entire subframes (i.e. they run until deadline enforcement) alongside SRTs to see SRT starvation and blocking.
- What to verify: SRTs should be prevented from running when HRTs monopolize the CPU; verify forced terminations for infinite HRTs.

### T10-mixed-2x10
- Purpose: mixed HRT + SRT scheduling within a medium-sized major frame.
- Scenario: Several HRTs and several SRTs spread across two subframes; SRTs run in leftover slots.
- What to verify: correct preemption of SRT by HRT, SRT execution in leftover windows, and correct HRT start/end behaviour.

### T11-mixed-1x20
- Purpose: single (20 ms) subframe mixed scenario.
- Scenario: HRTs and multiple SRTs configured inside a single subframe of 20 ms.
- What to verify: HRTs take their windows and SRTs occupy leftover time; verify proper preemption and ordering inside the long subframe.

### T12-mixed-1x40
- Purpose: single (40 ms) subframe mixed scenario.
- Scenario: longer subframe with several long and short HRTs plus SRTs.
- What to verify: SRTs run in leftover time between HRTs; HRT deadline enforcement across a large minor frame.

### T13-mixed_stress-8x5
- Purpose: stress test with many short subframes.
- Scenario: loop-created HRTs and SRTs in each of many (8) small subframes to increase context switching and scheduling frequency.
- What to verify: scheduler stability under high-frequency HRT activations and many SRTs; check for scheduling correctness and proper instance restarts.

### T14-mixed_stress-2x20
- Purpose: stress test with fewer but longer subframes.
- Scenario: multiple HRTs and SRTs in two long subframes to exercise longer-running HRTs mixed with several SRTs.
- What to verify: consistent deadline handling, SRT scheduling in leftover intervals and correct behaviour with larger subframe durations.

### T15-mixed_stress-1x40
- Purpose: single large subframe stress.
- Scenario: one huge subframe containing several HRTs spaced across the interval and multiple SRTs.
- What to verify: scheduler must correctly sequence short/long HRTs and interleave SRTs where time permits.

### T16-hrt_overlapping-1x10
- Purpose: overlapping HRT windows.
- Scenario: multiple HRT tasks are submitted with start/end times that overlap with an already accepted HRT task within the same subframe.
- What to verify: scheduler correctly manages overlapping HRTs in all possible scenarios (left overlapping, center overlapping, right overlapping, wrap overlapping), either by rejecting the tasks or by not scheduling them, without affecting system stability.

### T17-non_existing_subframe-1x10
- Purpose: invalid subframe assignment.
- Scenario: HRT/SRT tasks are assigned to subframes that do not exist in the current major frame configuration.
- What to verify: scheduler properly handles invalid subframe assignments, either by rejecting the task or by not scheduling it, without affecting system stability.

### T18-hrt_overlap_subframe_end-2x10
- Purpose: HRT window crossing subframe boundaries.
- Scenario: HRT tasks are configured with end times that extend beyond the end of their assigned subframe, overlapping into the next subframe.
- What to verify: scheduler correctly handles HRTs that overlap subframe boundaries, either by rejecting the task or by not scheduling it, without affecting system stability.

### T19-hrt_startTime_geq_endTime-1x10
- Purpose: invalid HRT window (start >= end).
- Scenario: HRT tasks are created with start times greater than or equal to their end times, representing an invalid configuration.
- What to verify: scheduler detects and correctly handles invalid HRT window configurations, either by rejecting the task or by not scheduling it, without affecting system stability.

## What to look for when you run a test
- `vPrintSubframes()` output — confirms your intended timeline and task placements.
- Task log prints like `[ <tick> ] <task-name> START/END` — verify start times and completion behaviour.
- Trace showing deadline misses (the scheduler calls `traceTASK_DEADLINE_MISS`) and the subsequent forced termination for HRT tasks that overrun.
- For restart tests: after a task is terminated at a deadline, verify the next scheduled instance restarts at its assigned window.
- For SRT tests: confirm SRT tasks only run when HRTs are not active; SRTs may be preempted mid-execution.
