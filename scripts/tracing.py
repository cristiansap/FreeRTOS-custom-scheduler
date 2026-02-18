import sys
import asyncio
import json
from enum import Enum

from graph import plot_gantt

TRACES = "--traces" in sys.argv
PRINTS = "--prints" in sys.argv

TARGET = sys.argv[1]
MAJORS = 8


class Task(Enum):
    END = "pause" 
    START = "start"
    COMPLETE = "complete"
    MISS = "terminate (deadline miss)"
    OVERFLOW = "terminate (subframe overflow)"


class TraceMonitor:
    def __init__(self, process, print_trace=False, print_setup=False, print_running=False):
        self.process = process

        self.log_traces = print_trace
        self.log_prints = print_setup
        self.log_runtime = print_running

        self.last_event = None
        self.parse_extra = None
        
        self.task_subframes = None
        self.subframe_duration = None

        self.output = None
        self.active = {}

    async def execute_capture(self, tick_limit=None, major_limit=None):
        self.output = []
        await self.execute(tick_limit, major_limit)
        return self.output

    async def execute(self, tick_limit=None, major_limit=None):
        self.tick_limit = tick_limit
        self.major_limit = major_limit

        async for line in self.process.stdout:
            try:
                self.read_line(line.decode().strip())
            except InterruptedError:
                self.process.terminate()
                await self.process.wait()
                return

    def read_line(self, line: str):
        if line.startswith("[TRACE]"):
            self.parse_trace(line)
            
        elif line.startswith("[TASKS]"):
            self.log_prints = self.log_runtime
            parts = line[8:].split(" ")
            self.subframe_duration = int(parts[0])
            self.task_subframes = json.loads(parts[1])
            
            if self.major_limit:
                majors = self.subframe_duration * len(self.task_subframes)
                self.tick_limit = 25000 * majors * self.major_limit

        else:
            if self.log_prints:
                print(line)
            if self.parse_extra:
                self.parse_extra(line)
        
    def parse_trace(self, line: str) -> bool:
        parts = line.split(" ")[1:]
        timing = int(parts[0])
        event = parts[1].replace("_END", "")
        ended = parts[1].endswith("END")
        name = event if event in ("SysTick", "PendSV") else parts[2]

        if self.log_traces:
            if event == "COMPLETE":
                self.print_trace(timing, name, Task.COMPLETE)
            if event == "MISS":
                self.print_trace(timing, name, Task.MISS)
            if event == "OVERFLOW":
                self.print_trace(timing, name, Task.OVERFLOW)
            if event == "TASK":
                status = Task.END if ended else Task.START
                self.print_trace(timing, name, status)
        
        if self.output is not None:
            if event == "MISS":
                self.output.append((timing, "MISS", timing))

            if event in ("TASK", "SysTick", "PendSV") and not ended:
                self.active[name] = len(self.output)
                self.output.append((timing, name, timing))
                
            if event in ("TASK", "SysTick", "PendSV") and ended:
                index = self.active.pop(name, None)
                if index is not None:
                    start, _, _ = self.output[index]
                    self.output[index] = (start, name, timing)
            
        if self.tick_limit and timing >= self.tick_limit:
            for name, index in self.active.items():
                start, _, _ = self.output[index]
                self.output[index] = (start, name, timing)
            raise InterruptedError()
        
    def print_trace(self, timing, task, event):
        if not self.last_event in (Task.MISS, Task.COMPLETE, Task.OVERFLOW):
            print(f"[{timing/25000:10.3f} ms ] {task} {event.value}")

        self.last_event = event

    def show_graph(self, splits=None, fix_t_max=None):
        tasks = []
        for i, subframe in enumerate(self.task_subframes):
            for _, start, end in subframe["HRT"]:
                base = 25000 * self.subframe_duration * i
                tasks.append((base + start*25000, base + end*25000))

        plot_gantt(self.output, splits=splits, fix_t_max=fix_t_max, tasks=tasks)


async def create_qemu_process(target):
    return await asyncio.create_subprocess_exec(
        "qemu-system-arm",
        "-M", "mps2-an385",
        "-icount", "shift=0,align=on",
        "-nographic",
        "-kernel", target,
        stdin=asyncio.subprocess.DEVNULL,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT)


async def main():
    qemu = await create_qemu_process(TARGET)
    monitor = TraceMonitor(qemu, print_setup=True, print_trace=TRACES, print_running=PRINTS)

    try:
        if "--graph" in sys.argv:
            await monitor.execute_capture(major_limit=MAJORS)
            monitor.show_graph(splits=MAJORS)
        else:
            await monitor.execute()
    finally:
        if qemu.returncode is None:
            qemu.terminate()
            await qemu.wait()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass