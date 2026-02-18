import sys
import asyncio
import shutil

if len(sys.argv) >= 2:
    TARGET, DURATION = sys.argv[1], 120

def create_logger(process, reader):
    async def read_output_lines(process):
        cache = []
        async for line in process.stdout:
            line = reader(line.decode().strip())
            if line:
                cache.append(line)
        return cache
    
    return asyncio.create_task(read_output_lines(process))


def pick_gdb_executable() -> str:
    # If debian -> gdb-multiarch, on Arch -> gdb
    for exe in ("gdb-multiarch", "gdb"):
        if shutil.which(exe):
            return exe
    raise FileNotFoundError("Neither 'gdb-multiarch' nor 'gdb' found in PATH")

async def create_gdb_process(target, cpu_ticks_limit):
    return await asyncio.create_subprocess_exec(
        pick_gdb_executable(),
        target,
        "-batch",
        "-ex", "target remote :1234",
        "-ex", "source scripts/debug.gdb",
        "-ex", f"tasklog {cpu_ticks_limit}",
        stdin=asyncio.subprocess.DEVNULL,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT)
    
async def create_qemu_process(target):
    return await asyncio.create_subprocess_exec(
        "qemu-system-arm", 
        "-M", "mps2-an385",
        "-icount", "shift=0,align=on",
        "-nographic",
        "-kernel", target,
        "-S", "-gdb", "tcp::1234",
        stdin=asyncio.subprocess.DEVNULL,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT)
    
def qemu_log(line):
    if not line.startswith("qemu-system-arm: terminating"):
        print(line)
        return line

def gdb_log(line):
    if line.startswith("[GDB]"):
        if line[6:10] in ("WARN", "FAIL"):
            print(line)
            return None

        parts = line[6:].split(" ") + ["N/A"]
        parts = line[6:].split(" ")

        if parts[1] == "TASK":
            task = parts[2] if len(parts)==3 else "N/A"
            return (int(parts[0]), "TASK", task)
    
        if parts[1] in ("SysTick", "PendSV", "PENDSVSET"):
            return (int(parts[0]), parts[1])
        
        if parts[0] in ("STARTED", "COMPLETED"):
            print(line)
            return parts[0]

async def run_capture_processes(target, cpu_ticks_limit):
    qemu = await create_qemu_process(target)
    gdb = await create_gdb_process(target, cpu_ticks_limit)

    qemu_reader = create_logger(qemu, reader=qemu_log)
    gdb_reader = create_logger(gdb, reader=gdb_log)

    try:
        gdb_output = await gdb_reader
        qemu.terminate()
        qemu_output = await qemu_reader

        return gdb_output, qemu_output
    except:
        qemu.kill()

def task_interrupt_ratio(events):
    task = 0
    interrupt = 0
    for start, name, end in events:
        if name not in ("PendSV", "SysTick"):
            task += end - start
        else:
            interrupt += end - start
    return task, interrupt, task + interrupt

def compute_end_times(data):
    gantt_data = []
    for event, next_event in zip(data[:-1], data[1:]):
        end = next_event[0]
        start = event[0]
        
        if event[1] in ("SysTick", "PendSV", "TASK"):
            name = event[2] if event[1] == "TASK" else event[1]
            gantt_data.append((start, name, end))
        else:
            gantt_data.append((start, event[1], start))
            
    return gantt_data

async def capture_traces():
    gdb, _ = await run_capture_processes(TARGET, DURATION)

    if gdb[0] != "STARTED" and gdb[-1] != "COMPLETED":
        return None

    gantt_data = compute_end_times(gdb[1:-1])

    if __name__ == "__main__":
        for line in gantt_data:
            print(line)

    task, interrupt, total = task_interrupt_ratio(gantt_data)
    print(f"Task: {task} ({task/total*100:.2f}%), ISR: {interrupt} ({interrupt/total*100:.2f}%)")

    return gantt_data

if __name__ == "__main__" and TARGET:
    asyncio.run(capture_traces())
