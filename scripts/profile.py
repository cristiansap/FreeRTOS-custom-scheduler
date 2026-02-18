import re
import inquirer
from pathlib import Path
from colorama import Fore, Style

C_IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
PROFILE_NAME_RE = re.compile(r'^[A-Za-z0-9_-]+$')



def print_error(msg):
    print(Fore.RED + msg + Style.RESET_ALL)

def print_success(msg):
    print(Fore.GREEN + msg + Style.RESET_ALL)

def print_info(msg):
    print(Fore.CYAN + msg + Style.RESET_ALL)

def find_profiles_dir() -> Path:
    start = Path(__file__).resolve().parent

    # 1) First: try to find an existing "profiles" folder in parents
    p = start
    while True:
        candidate = p / "profiles"
        if candidate.is_dir():
            return candidate
        if p.parent == p:  # root filesystem
            break
        p = p.parent

    # 2) Not found: create it under the project root (= parent of "scripts" dir)
    p = start
    while True:
        if p.name == "scripts":
            project_root = p.parent
            profiles_dir = project_root / "profiles"
            profiles_dir.mkdir(parents=True, exist_ok=True)
            return profiles_dir
        if p.parent == p:
            break
        p = p.parent

    raise FileNotFoundError(
        "Could not find an existing 'profiles' folder, and could not locate project root "
        "(expected this script to be under a 'scripts/' directory)."
    )

def get_next_profile_dir(profiles_dir: Path) -> Path:
    i = 0
    while True:
        path = profiles_dir / f"python-profile{i}"
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            return path
        i += 1

def validate_profile_name(name: str, profiles_dir: Path) -> str | None:
    if not name:
        return "Profile name cannot be empty."

    if name in (".", ".."):
        return "Profile name cannot be '.' or '..'."
    
    if not PROFILE_NAME_RE.match(name):
        return "Profile name may contain only letters, numbers, '_' and '-'."

    target = profiles_dir / name
    if target.exists():
        return f"Profile '{name}' already exists."

    return None

# Keeps asking until a valid, non-existing profile dir name is provided.
def prompt_profile_dir(profiles_dir: Path) -> Path | None:
    while True:
        ans = inquirer.prompt(
            [inquirer.Text("name", message="Insert new profile name (folder name)")],
            raise_keyboard_interrupt=False,
        )

        # user pressed ESC / cancelled
        if not ans:
            print_info("\nCancelled. Profile not created.\n")
            return None

        name = (ans.get("name") or "").strip()
        err = validate_profile_name(name, profiles_dir)

        if err:
            print_error(f"\nInvalid profile name: {err}\n")
            continue

        path = profiles_dir / name
        try:
            path.mkdir(parents=True, exist_ok=False)
        except FileExistsError:
            # race condition / edge-case: created between exists() and mkdir()
            print_error(f"\nInvalid profile name: Profile '{name}' already exists.\n")
            continue

        return path


# Writes CustomConfig.h
def write_alloc_config(profile_dir: Path,
                       static_val: int,
                       dynamic_val: int,
                       subframe_count_per_major: int,
                       subframe_duration_ms: int,
    ) -> Path:

    task_config_path = profile_dir / "CustomConfig.h"
    with open(task_config_path, "w", encoding="utf-8") as f:
        f.write(f"#define configSUPPORT_STATIC_ALLOCATION          {static_val}\n")
        f.write(f"#define configSUPPORT_DYNAMIC_ALLOCATION         {dynamic_val}\n\n")
        f.write(f"#define configSUBFRAME_COUNT_PER_MAJOR           {subframe_count_per_major}\n")
        f.write(f"#define configSUBFRAME_DURATION                  pdMS_TO_TICKS({subframe_duration_ms})\n")
    return task_config_path

def select_subframe_per_major() -> int:
    q = [inquirer.Text("count", message="Insert number of subframes per major (integer >= 1)", default="4")]
    a = inquirer.prompt(q) or {}
    s = (a.get("count") or "").strip()
    if not s.isdigit() or int(s) < 1:
        print_error("\n Invalid value. \n")
        return 4
    return int(s)

def select_subframe_duration_ms() -> int:
    q = [inquirer.Text("ms", message="Insert subframe duration in ms (integer >= 1)", default="10")]
    a = inquirer.prompt(q) or {}
    s = (a.get("ms") or "").strip()
    if not s.isdigit() or int(s) < 1:
        print_error("\n Invalid value. \n")
        return 10
    return int(s)

def write_setup_c(profile_dir: Path, allocation: str, hrt_tasks: list[dict], srt_tasks: list[dict]) -> Path:
    use_static = (allocation == "Static")
    setup_path = profile_dir / "setup.c"

    with open(setup_path, "w", encoding="utf-8") as f:
        f.write('#include "FreeRTOS.h"\n')
        f.write('#include "setup.h"\n')
        f.write('#include "task.h"\n\n')

        if use_static and (hrt_tasks or srt_tasks):
            f.write("// Static allocation buffers\n")
            for t in hrt_tasks:
                f.write(f"static HRTTask_t {t['buffer_name']};\n")
            for t in srt_tasks:
                f.write(f"static SRTTask_t {t['buffer_name']};\n")
            f.write("\n")

        if hrt_tasks or srt_tasks:
            f.write("// Task handles\n")
            for t in hrt_tasks:
                f.write(f"static HRTHandle_t {t['handle_name']} = NULL;\n")
            if use_static:
                for t in srt_tasks:
                    f.write(f"static SRTHandle_t {t.get('handle_name', f'xSrtHandle{0}')} = NULL;\n")
            f.write("\n")
        
        funcs = set() # same function might be used in multiple tasks, so we use a set to avoid duplicates
        funcs.update(t["pxTaskCode"] for t in hrt_tasks)
        funcs.update(t["pxTaskCode"] for t in srt_tasks)

        if funcs:
            f.write("// Task function prototypes\n")
            for func in sorted(funcs):
                f.write(f"void {func}(void *pvParameters);\n")
    
        f.write("\n")
        f.write("void PROFILE_setup(void)\n{\n")

        if not hrt_tasks and not srt_tasks:
            f.write("    // No tasks configured.\n")
        else:
            if hrt_tasks:
                f.write("    // HRT tasks\n")
                for t in hrt_tasks:
                    c_name = t["pcName"].replace('"', '\\"')
                    if use_static:
                        f.write(
                            f"    {t['handle_name']} = xTaskHrtCreateStatic("
                            f"{t['pxTaskCode']}, \"{c_name}\", {t['pvParameters']}, "
                            f"{t['ulSubframeId']}, {t['ulStartTime']}, {t['ulEndTime']}, "
                            f"&{t['buffer_name']}"
                            f");\n"
                        )
                    else:
                        f.write(
                            f"    xTaskHrtCreate("
                            f"{t['pxTaskCode']}, \"{c_name}\", {t['pvParameters']}, "
                            f"{t['ulSubframeId']}, {t['ulStartTime']}, {t['ulEndTime']}, "
                            f"&{t['handle_name']}"
                            f");\n"
                        )
                f.write("\n")

            if srt_tasks:
                f.write("    // SRT tasks\n")
                for t in srt_tasks:
                    c_name = t["pcName"].replace('"', '\\"')
                    if use_static:
                        handle_name = t["handle_name"]
                        f.write(
                            f"    {handle_name} = xTaskSrtCreateStatic("
                            f"{t['pxTaskCode']}, \"{c_name}\", {t['pvParameters']}, "
                            f"{t['ulSubframeId']}, &{t['buffer_name']}"
                            f");\n"
                        )
                    else:
                        f.write(
                            f"    xTaskSrtCreate("
                            f"{t['pxTaskCode']}, \"{c_name}\", {t['pvParameters']}, "
                            f"{t['ulSubframeId']}, NULL"
                            f");\n"
                        )

        f.write("}\n\n")

        if funcs:
            f.write("// Task function\n")
            for func in sorted(funcs):
                f.write(
                    f"void {func}(void *pvParameters) {{\n"
                    "\n"
                    "}\n\n"
                )

    return setup_path


def allocation_type():
    questions = [
        inquirer.List('allocation',
                          message= "Select which type of allocation you want to use (select with enter)",
                          choices=['Static', 'Dynamic'],
                        ),
    ]
    answers = inquirer.prompt(questions) or {}
    allocation = answers["allocation"]
    static_val = 1 if "Static" in allocation else 0
    dynamic_val = 1 if "Dynamic" in allocation else 0
    return allocation, static_val, dynamic_val

def add_HRT_task(hrt_tasks: list[dict], allocation: str, subframe_count_per_major: int, subframe_duration_ms: int):
    idx = len(hrt_tasks)

    questions = [
        inquirer.Text("pxTaskCode", message="Task function name (TaskFunction_t)"),
        inquirer.Text("pcName", message="Task name string"),
        inquirer.Text("pvParameters", message="pvParameters", default="NULL"),
        inquirer.Text("ulSubframeId", message="Subframe ID (uint32_t)"),
        inquirer.Text("ulStartTime", message="Start time (uint32_t)"),
        inquirer.Text("ulEndTime", message="End time (uint32_t)"),
    ]

    answers = inquirer.prompt(questions) or {}

    pxTaskCode = (answers.get("pxTaskCode") or "").strip()
    if not C_IDENT.match(pxTaskCode):
        print_error("\n Invalid task function name. \n")
        return

    pcName = (answers.get("pcName") or "").strip()
    if not pcName:
        print_error("\n Task name cannot be empty. \n")
        return

    pvParameters = (answers.get("pvParameters") or "NULL").strip() or "NULL"

    def parse_uint32(field):
        value = (answers.get(field) or "").strip()
        if not value.isdigit():
            print_error(f"\n {field} must be a non-negative integer. \n")
            return None
        return int(value)

    ulSubframeId = parse_uint32("ulSubframeId")
    ulStartTime = parse_uint32("ulStartTime")
    ulEndTime = parse_uint32("ulEndTime")

    if ulSubframeId is None or ulStartTime is None or ulEndTime is None:
        print_error("\n Invalid numeric input. \n")
        return

    if ulEndTime <= ulStartTime:
        print_error("\n End time must be greater than start time. \n")
        return
    if ulEndTime > subframe_duration_ms:
        print_error(f"\n End time must be less than subframe duration ({subframe_duration_ms} ms). \n")
        return
    if ulSubframeId >= subframe_count_per_major:
        print_error(f"\n Subframe ID must be less than subframe count per major ({subframe_count_per_major}). \n")
        return

    handle_name = f"xHrtHandle{idx}"

    task = {
        "pxTaskCode": pxTaskCode,
        "pcName": pcName,
        "pvParameters": pvParameters,
        "ulSubframeId": ulSubframeId,
        "ulStartTime": ulStartTime,
        "ulEndTime": ulEndTime,
        "handle_name": handle_name,
    }

    if allocation == "Static":
        task["buffer_name"] = f"xHrtTaskBuffer{idx}"
    
    # Overlap check within the same subframe: [start, end)
    for t in hrt_tasks:
        if t["ulSubframeId"] != ulSubframeId:
            continue
        
        existing_start = t["ulStartTime"]
        existing_end = t["ulEndTime"]

        # DON'T overlap if new_end <= old_start or new_start >= old_end 
        if ulStartTime < existing_end and ulEndTime > existing_start:
            print_error(
                f"\n Overlap detected in subframe {ulSubframeId}: "
                f"new [{ulStartTime}, {ulEndTime}) overlaps with "
                f"task '{t.get('pcName', '')}' [{existing_start}, {existing_end}). \n"
            )
            return

    hrt_tasks.append(task)
    print_success(f"\n HRT task {idx} successfully added. \n")

def add_SRT_task(srt_tasks: list[dict], allocation: str, subframe_count_per_major: int):
    idx = len(srt_tasks)

    questions = [
        inquirer.Text("pxTaskCode", message="Task function name (TaskFunction_t)"),
        inquirer.Text("pcName", message="Task name string"),
        inquirer.Text("pvParameters", message="pvParameters", default="NULL"),
        inquirer.Text("ulSubframeId", message="Subframe ID (uint32_t)"),
    ]

    answers = inquirer.prompt(questions) or {}

    pxTaskCode = (answers.get("pxTaskCode") or "").strip()
    if not C_IDENT.match(pxTaskCode):
        print_error("\n Invalid task function name. \n")
        return

    pcName = (answers.get("pcName") or "").strip()
    if not pcName:
        print_error("\n Task name cannot be empty. \n")
        return

    pvParameters = (answers.get("pvParameters") or "NULL").strip() or "NULL"

    value = (answers.get("ulSubframeId") or "").strip()
    if not value.isdigit():
        print_error("\n ulSubframeId must be a non-negative integer. \n")
        return
    ulSubframeId = int(value)

    if ulSubframeId >= subframe_count_per_major:
        print_error(f"\n Subframe ID must be less than subframe count per major ({subframe_count_per_major}). \n")
        return

    task = {
        "pxTaskCode": pxTaskCode,
        "pcName": pcName,
        "pvParameters": pvParameters,
        "ulSubframeId": ulSubframeId,
    }

    if allocation == "Static":
        task["buffer_name"] = f"xSrtTaskBuffer{idx}"
        task["handle_name"] = f"xSrtHandle{idx}"

    srt_tasks.append(task)
    print_success(f"\n SRT task {idx} successfully added. \n")

def main():
    allocation, static_val, dynamic_val = allocation_type()

    subframe_count_per_major = select_subframe_per_major()
    subframe_duration_ms = select_subframe_duration_ms()
    

    hrt_tasks: list[dict] = []
    srt_tasks: list[dict] = []

    while True:
        questions = [
            inquirer.List('choice',
                message='What do you want to do (select with "enter")?',
                choices=['Create new HRT task',
                         'Create new SRT task',
                         'Save and exit',
                         'Exit without saving'
                        ]
            )
        ]
        answers = inquirer.prompt(questions)

        if not answers:
            return        
        elif answers['choice'] == 'Create new HRT task':
            print_info("\n Creating new HRT task...")
            add_HRT_task(hrt_tasks, allocation, subframe_count_per_major, subframe_duration_ms )
        elif answers['choice'] == 'Create new SRT task':
            print_info("\n Creating new SRT task...")
            add_SRT_task(srt_tasks, allocation, subframe_count_per_major)
        elif answers['choice'] == 'Save and exit':
            print_info("\n Saving and exiting... \n")
            profiles_dir = find_profiles_dir() # finds the profiles directory
            next_profile_dir = prompt_profile_dir(profiles_dir)
            if next_profile_dir is None:
                continue

            task_config_path = write_alloc_config(next_profile_dir, static_val, dynamic_val, subframe_count_per_major, subframe_duration_ms)
            setup_path = write_setup_c(next_profile_dir, allocation, hrt_tasks, srt_tasks)

            print_success(f"\nSaved: {task_config_path}")
            print_success(f"Saved: {setup_path}")
            print_info("Goodbye! \n")
            return
        elif answers['choice'] == 'Exit without saving':
            questions = [
                inquirer.List('exit without saving',
                              message = "Are you sure you want to quit? All your progress will be lost.",
                              choices=['Yes', 'No'],
                              default="No",
                              )                
            ]
            answers = inquirer.prompt(questions)
            if(answers['exit without saving'] == 'Yes'):
                print_info("\n Exiting without saving... \n")
                return
                        
if __name__ == "__main__":    
    main()

