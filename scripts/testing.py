import json
import sys
import asyncio
from pathlib import Path
from itertools import chain

import inquirer
from colorama import Fore, Style

from graph import plot_gantt
from tracing import create_qemu_process, TraceMonitor

TESTS = sys.argv[1:]
TICKS_PER_MS = 25000
TOLERANCE = TICKS_PER_MS // 20

def _overlaps(a_start, a_end, b_start, b_end):
    return a_start < b_end and a_end > b_start

def check_hrt_runs_once_per_subframe(traces, task_subframes, subframe_duration_ms, major_limit):
    sf_ticks = TICKS_PER_MS * subframe_duration_ms
    major_ticks = sf_ticks * len(task_subframes)

    subframe_hrts = [subframe["HRT"] for subframe in task_subframes]

    schedule = []
    for i, tasks in enumerate(subframe_hrts):
        subframe_s = sf_ticks * i
        schedule.append({name: (subframe_s + s*TICKS_PER_MS,subframe_s + e*TICKS_PER_MS) for name, s, e in tasks})

    hrt_names = set(chain.from_iterable(x.keys() for x in schedule))
    if not hrt_names:
        return True
    hrt_traces = [(s,name,e) for (s,name,e) in traces if name in hrt_names]
    hrt_bursts = {name: 0 for name in hrt_names} # count number of task burts

    for s, name, e in hrt_traces:
        sf = (s % major_ticks) // sf_ticks

        if name not in schedule[sf]:
            print(f"  {Fore.RED}FAIL{Style.RESET_ALL} - HRT '{name}' started outside subframe {sf}")
            return False
        
        major_s = hrt_bursts[name] * major_ticks
        task_start, task_end = schedule[sf][name]

        if s > major_s + task_start + TOLERANCE:
            print(f"  {Fore.RED}FAIL{Style.RESET_ALL} - HRT '{name}' started after maximum tolerance")
            return False

        if e > major_s + task_end + TOLERANCE:
            print(f"  {Fore.RED}FAIL{Style.RESET_ALL} - HRT '{name}' run after deadline + tolerance")
            return False

        hrt_bursts[name] += 1
    
    print(f"  {Fore.GREEN}PASS{Style.RESET_ALL} - HRT tasks run in expected time regions")

    for name, count in hrt_bursts.items():
        if count != major_limit:
            print(f"  {Fore.RED}FAIL{Style.RESET_ALL} - HRT '{name}' ran {count} out of {major_limit} majors")
            return False

    print(f"  {Fore.GREEN}PASS{Style.RESET_ALL} - HRT tasks run exactly once per subframe")
    return True

def check_srt_order_and_subframe(traces, task_subframes, subframe_duration_ms, major_limit):
    sf_ticks = TICKS_PER_MS * subframe_duration_ms
    major_ticks = sf_ticks * len(task_subframes)

    expected = [subframe["SRT"] for subframe in task_subframes]
    expected_all = set(name for srt_list in expected for name in srt_list)
    if not expected_all:
        return True
    srt_traces = [(s,name,e) for (s,name,e) in traces if name in expected_all]
    ran_tasks = {}

    for s, name, e in srt_traces:
        major_idx = s // major_ticks
        if major_idx >= major_limit:
            continue

        sf = (s % major_ticks) // sf_ticks

        # SRT must not start in a subframe where it's not configured
        if name not in expected[sf]:
            print(f"  {Fore.RED}FAIL{Style.RESET_ALL} - SRT '{name}' started outside subframe {sf}")
            return False

        task_end = major_idx * major_ticks + sf * sf_ticks + sf_ticks 

        if e > task_end + TOLERANCE:
            print(f"  {Fore.RED}FAIL{Style.RESET_ALL} - SRT '{name}' run after subframe end + tolerance")
            return False
        

        key = (major_idx, sf)
        ran_tasks.setdefault(key, []).append(name)
                
    print(f"  {Fore.GREEN}PASS{Style.RESET_ALL} - SRT tasks run in expected subframes")

    # Verify order for each captured (major, subframe); partial execution is allowed
    for (major_idx, sf), bucket in ran_tasks.items():
        expected_list = expected[sf]
        indices = [expected_list.index(x) for x in bucket]  
        
        for i in range(len(indices) - 1):
            if indices[i] != indices[i + 1] and indices[i]+1 != indices[i + 1]:
                print(f"  {Fore.RED}FAIL{Style.RESET_ALL} - SRTs {bucket[i]} and {bucket[i+1]} run out of order")
                return False

    print(f"  {Fore.GREEN}PASS{Style.RESET_ALL} - SRT tasks run in expected order")
    return True


def check_scheduler_overhead(traces, task_subframes, subframe_duration_ms, major_limit):
    sf_ticks = TICKS_PER_MS * subframe_duration_ms
    major_ticks = sf_ticks * len(task_subframes)
    total_ticks = major_limit * major_ticks
    overhead_ticks = 0
    for s, name, e in traces:
        if name in ("SysTick", "PendSV"):
            overhead_ticks += e - s
    
    overhead_radio = overhead_ticks/total_ticks
    if overhead_radio > 0.08:
        print(f"  {Fore.RED}FAIL{Style.RESET_ALL} - Scheduler overhead is {overhead_radio*100:.2f}% of total time")
        return False

    print(f"  {Fore.GREEN}PASS{Style.RESET_ALL} - Scheduler overhead is {overhead_radio*100:.2f}% of total time")
    return True


def traces_checks(traces, subframe_tasks, duration, major_limit):
    if not check_hrt_runs_once_per_subframe(traces, subframe_tasks, duration, major_limit):
        return False

    if not check_srt_order_and_subframe(traces, subframe_tasks, duration, major_limit):
        return False
    
    if not check_scheduler_overhead(traces, subframe_tasks, duration, major_limit):
        return False
    
    return True


async def run_test_process(target):
    monitor = TraceMonitor(await create_qemu_process(target))
    assert_ok = True
    major_limit = 2

    def parse_test_asserts(line):
        nonlocal assert_ok
        nonlocal major_limit
        if line.startswith("[PASS]"):
            print(f"  {Fore.GREEN}PASS{Style.RESET_ALL} - {line[7:]}")
            major_limit = 0
        if line.startswith("[FAIL]"):
            print(f"  {Fore.RED}FAIL{Style.RESET_ALL} - {line[7:]}")
            assert_ok = False
            raise InterruptedError

    monitor.parse_extra = parse_test_asserts
    traces = await monitor.execute_capture(major_limit=major_limit)
    setup = monitor.task_subframes
    duration = monitor.subframe_duration
    
    if major_limit > 0 and assert_ok:
        test_ok = traces_checks(traces, setup, duration, major_limit)
    else:
        test_ok = assert_ok

    print()

    if not test_ok:
        question = inquirer.Confirm('proceed', message="Do you want to show trace graph?")
        confirm = inquirer.prompt([question])["proceed"]

        if confirm:
            cpu_ticks = 25000 * duration * len(setup) * major_limit # extend unfinished graph
            monitor.show_graph(fix_t_max=cpu_ticks, splits=(2 * len(setup)))

    return test_ok


async def main():
    print(f"{Fore.BLUE}{'-'*44}")
    print(f"{Fore.BLUE}| {Style.BRIGHT}Started realtime scheduler testing suite {Style.NORMAL}|")
    print(f"{Fore.BLUE}{'-'*44}{Style.RESET_ALL}")

    for target in TESTS:
        full_name = Path(target).parent.name
        id, test_name, timing = full_name.split("-")

        print(f"{Fore.WHITE}[{id[1:]}] Running {Style.BRIGHT}\"{test_name}\"{Style.NORMAL} ({timing})")
        test_ok = await run_test_process(target)

        if not test_ok:
            break
    
    if test_ok:
        print(f"Successfully ran {len(TESTS)} test cases.")
    else:
        print(f"Stopped at failing test.")
    

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass