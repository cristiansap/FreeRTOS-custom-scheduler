# Precise Scheduler for FreeRTOS

## Overview
This project extends FreeRTOS with a **deterministic, timeline-driven scheduler** designed for real-time systems.

The standard priority-based preemptive scheduling is extended adopting a **time-triggered architecture** based on:

- A **Major Frame**
- A fixed number of **Subframes**
- Predefined execution slots for tasks

At the end of each major frame, the scheduler **replays the same timeline**, guaranteeing deterministic repetition across different major frames.

This approach is particularly suited for systems where strict timing constraints and predictability are required.

## Scheduler Architecture

### Major Frame - Subframe Model

- The scheduler operates within a major frame, whose duration is defined at compile time (e.g., 100 ms, 1 s)
- Each major frame is divided into multiple subframes
- Each subframe contains a predefined set of tasks with assigned timing and execution order

Task activation, execution order, and timing constraints are defined before the scheduler starts, ensuring repeatable and predictable execution.

## Task Classes

### Hard Real-Time (HRT) Tasks

HRT tasks are executed in **fixed time slots** inside specific subframes. For each HRT task, the scheduler knows:
-  `ulSubframeId`: the identifier of the subframe the task is assigned to 
-  `ulStartTime` and `ulEndTime` (relative to the specific subframe):


    - The start time is the exact release time in the specific subframe
    - The task runs until completion if it finishes before the end time
    - The task is forcibly terminated if it exceeds its deadline

Note: HRT tasks are non-preemptive once started (except for deadline enforcement).

### Soft Real-Time (SRT) Tasks

SRT tasks execute during the **idle time left by HRT tasks** inside subframes.

Key features:

- Scheduled in a fixed order (e.g., Task_X → Task_Y → Task_Z)
- Preemptible by HRT tasks at any time
- Best-effort execution (no deadline guarantees)

---

## Profiles & Configuration Model 

The build system allows the user to define **profiles** providing a runtime configuration for the scheduler. Profiles define:

- The **major frame** and its **subframe topology** (count and duration)
- The **allocation type** (static or dynamic) for tasks and internal scheduler structures
- The set of **Hard Real-Time (HRT)** and **Soft Real-Time (SRT)** tasks with their execution parameters 

Profile files are stored under `profiles/<profile-name>/` and consist of:

- `CustomConfig.h` — profile-specific macros for subframe timing, allocation flags, and other settings
- `setup.c` — C source file that instantiates tasks according to the chosen allocation strategy

Profiles allow you to quickly switch between different scheduler configurations **without changing source code**.

### Creating a Profile (Interactive Tool)

You can create a new scheduler profile using the interactive Python configuration framework:

```bash
make profile
```

The script will guide you through:

- Selecting allocation type (Static or Dynamic)
- The major frame and subframe topology
- Adding HRT and SRT tasks with their parameters

When you choose **Save and exit**, you will be prompted to select a profile name, and a new folder with that name will be created under `profiles/`.

### Profile build system

User generated profiles are automatically included in the Makefile build rules.
This workflow allows iterative profile development: you can adjust HRT/SRT tasks, timeline parameters, allocation strategies and immediately test or trace the resulting schedule

The following command performs compilation and execution of both `CustomConfig.h` and `setup.c` from the selected profile:
```bash
make run PROFILE=<profile-name>
```
Note: profile object files are linked against FreeRTOS, recompiling only `tasks.c` with the respective profile's `CustomConfig.h`.

### Tracing & Debugging

To capture runtime traces for offline analysis (without interactive execution), use:

```bash
make trace PROFILE=<profile-name>
```

This target leverages the trace macros defined in `tracingConfig.h` to log HRT/SRT events and system ticks in a structured format.

Alternatively, more debugging information can be collected by running the following command, leveraging `gdb`:
```bash
make debug PROFILE=<profile-name>
```

### Gantt Chart Visualization

It is possible to generate a graph starting from data obtained with `trace` or `debug`, running:

```bash
make trace_graph PROFILE=<profile-name>
# or
make debug_graph PROFILE=<profile-name>
```

## Makefile Summary

The Makefile supports several targets for running, debugging, and analyzing the scheduler. All targets that depend on profiles require `PROFILE=<profile-name>` argument. Alternatively, you can also use `TEST=<test-name>` to run specific tests.

### Profile-Dependent Targets

| Target | Description |
| --- | --- |
| `make run` | Builds and runs the scheduler for the selected profile or test. |
| `make trace` | Executes the scheduler with tracing enabled, logging task and system tick events using the trace macros. |
| `make debug` | Runs the scheduler in debug mode, performing temporal checks and runtime assertions on HRT and SRT tasks. |
| `make trace_graph` | Generates a graphical representation of the execution timeline using captured trace logs. |
| `make debug_graph` | Runs the scheduler in debug mode and produces a timeline graph of task execution and temporal checks. |

### Profile-Independent Targets

| Target | Description |
| --- | --- |
| `make test` | Runs all available test cases without requiring a specific profile. Useful for verifying scheduler correctness. |
| `make profile` | Launches the interactive Python configuration framework to create or edit a profile. Generates `CustomConfig.h` and `setup.c` in the `profiles/` directory. |
| `make clean` | Clean up the build output folder. |

---

## Dependencies

The interactive scripts require Python 3.9+ version and a couple of additional packages. The simplest way to install them is with a virtual environment and the provided `requirements.txt`, running the following commands:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## User API Reference
This section summarizes the APIs exposed to the user to configure and use the custom scheduler. The goal is to keep the interface as close as possible to standard FreeRTOS conventions, while enabling deterministic scheduling through HRT and SRT tasks.

### Hard Real-Time (HRT) Task APIs

---

```c
BaseType_t xTaskHrtCreate(
    TaskFunction_t pxTaskCode,
    const char *pcName,
    void *pvParameters,
    uint32_t ulSubframeId,
    uint32_t ulStartTime,
    uint32_t ulEndTime,
    HRTHandle_t *pxCreatedTask
);
```
This API creates a **Hard Real-Time** task scheduled inside a specific subframe of the major frame. The task is released exactly at `ulStartTime` and must finish within `ulEndTime`. If the deadline is exceeded, the task is terminated.

---

```c
BaseType_t xTaskHrtCreateStatic(
    TaskFunction_t pxTaskCode,
    const char *pcName,
    void *pvParameters,
    uint32_t ulSubframeId,
    uint32_t ulStartTime,
    uint32_t ulEndTime,
    HRTTask_t *pxTaskBuffer
);
```
This is the **static version** of ```xTaskHrtCreate()```, allowing the user to provide memory explicitly and avoid dynamic allocation.

### Soft Real-Time (SRT) Task APIs
---

```c
BaseType_t xTaskSrtCreate(
    TaskFunction_t pxTaskCode,
    const char *pcName,
    void *pvParameters,
    TaskHandle_t *pxCreatedTask
);
```
This API creates a **Soft Real-Time** task that executes during the idle time left by HRT tasks. Note that there is no start or end time, since SRT tasks are executed only when no HRT task is active.

---

```c
BaseType_t xTaskSrtCreateStatic(
    TaskFunction_t pxTaskCode,
    const char *pcName,
    void *pvParameters,
    StaticTask_t *pxTaskBuffer
);
```
This is the **static version** of ```xTaskSrtCreate()```, allowing the user to provide memory explicitly and avoid dynamic allocation.


### Utility APIs

---

```c
void vPrintSubframes(void);
```
This API prints the configured major frame, subframes, and associated HRT/SRT tasks. It is useful for debugging and verifying the correctness of the timeline configuration.

---

```c
void vPrintSubframesJson(void);
```
This API prints the configured major frame, subframes, and associated HRT/SRT tasks in JSON format.

### Start Scheduler API

```c
void vTaskStartScheduler(void);
```

This API has been modified to launch the custom scheduler. It relies upon existing FreeRTOS API, enriching its standard functionality.

## Scheduler Configuration Macros

This section lists the configuration macros used to **enable and tune** the timeline-driven scheduler. They control which sub-systems are active (HRT vs SRT), the major frame - subframe topology, memory allocation modes, task stack sizes and priorities, and debug helpers. Many of these macros live in profile-specific headers or in the project's `config/` files and **should be set per-profile** to reflect the timing and resource needs of your application.

| Macro / Group | Purpose | Example / Typical value | Notes |
| --- | --- | ---: | --- |
| `configENABLE_HRT_SCHEDULER` | Enable Hard Real-Time (HRT) scheduler support. | `1` / `0` | When enabled, HRT task creation APIs are available. Can be used independently of SRT. |
| `configENABLE_SRT_SCHEDULER` | Enable Soft Real-Time (SRT) scheduler support. | `1` / `0` | When enabled, SRT task creation APIs are available. Can be used independently of HRT. |
| `configSUBFRAME_COUNT_PER_MAJOR` | Number of subframes per major frame. | `4`, `10`, `20`, etc. | Combined with `configSUBFRAME_DURATION` to define the major frame duration. |
| `configSUBFRAME_DURATION` | Duration of each subframe (milliseconds). | `25`, `100`, etc. | Major frame = `configSUBFRAME_COUNT_PER_MAJOR * configSUBFRAME_DURATION`. Set in ms at compile-time. |
| `configSUPPORT_STATIC_ALLOCATION` | Enable static task allocation support (standard FreeRTOS config). | `1` / `0` | If enabled, the static APIs may be used to avoid dynamic heap usage. |
| `configSUPPORT_DYNAMIC_ALLOCATION` | Enable dynamic task allocation support (standard FreeRTOS config). | `1` / `0` | If enabled, dynamic task creation APIs are available. |
| `configKERNEL_PROVIDED_STATIC_MEMORY` | When enabled, kernel supplies application static memory buffers. | `1` / `0` | If enabled, the kernel internally defines static stack memory for HRT/SRT tasks. It requires the user to define `configHRT_TASKS_STACK_SIZE` and `configSRT_TASKS_STACK_SIZE` if the corresponding HRT/SRT functionalities are enabled. |
| `configHRT_TASKS_STACK_SIZE` | Stack size for HRT tasks (words/bytes depending on port). | `configMINIMAL_STACK_SIZE * 2` | Size used to define stack memory **shared** by all HRT tasks. |
| `configSRT_TASKS_STACK_SIZE` | Stack size for SRT tasks (words/bytes depending on port). | `configMINIMAL_STACK_SIZE` | Size used to define stack memory **shared** by all SRT tasks. |
| `configHRT_TASKS_PRIORITY` | Priority assigned internally by the scheduler to all HRT tasks. | `configMAX_PRIORITIES - 1` | HRT tasks should be higher priority than SRT taks. |
| `configSRT_TASKS_PRIORITY` | Priority assigned internally by the scheduler to all SRT tasks. | `tskIDLE_PRIORITY + 1` | SRT tasks should be lower priority than HRT tasks. |
| `INCLUDE_vPrintSubframes` | Enable printing of configured subframes (human-readable). | `1` / `0` | Debugging flag — not intended for production builds. |
| `INCLUDE_vPrintSubframesJson` | Enable printing subframes in JSON format. | `1` / `0` | Useful for automated parsing during testing — unsafe escaping, thus not intended for production builds. |

## Best practices and Suggestions

- Use the printable timeline (`vPrintSubframes()` or the JSON flag) during development to verify that timeline definitions and task placements match expectations
- Prefer static allocation if there is no real need to include heap allocation functionality
- Keep profile names and generated files under `profiles/` so they can be run with the corresponding `make` commands

## Example Configuration

### CustomConfig.h
```c
#define configSUPPORT_STATIC_ALLOCATION 0
#define configSUPPORT_DYNAMIC_ALLOCATION 1

#define configSUBFRAME_COUNT_PER_MAJOR 1
#define configSUBFRAME_DURATION pdMS_TO_TICKS(10)
```

### setup.c
```c
void PROFILE_setup(void)
{
    /* HRT tasks */
    xTaskHrtCreate(controlTask, "HRT_Control", NULL, 0, 0, 3, NULL);
    xTaskHrtCreate(actuatorTask, "HRT_Actuator", NULL, 0, 7, 10, NULL);
    
    /* SRT tasks */
    xTaskSrtCreate(backgroundTask, "SRT-background", NULL, 0, NULL);

    vPrintSubframes();
}
```

### Example Output
This is an output obtained by running `make trace` with the above configuration: 

```text
=== Subframe 0 ===
HRT count: 2
HRT[0]: HRT_Control | Start: 0 | End: 3
HRT[1]: HRT_Actuator | Start: 7 | End: 10
SRT count: 1
SRT[0]: SRT-background

[     0.000 ms ] HRT_Control start
[     2.230 ms ] HRT_Control complete
[     2.236 ms ] SRT-background start
[     3.481 ms ] SRT-background complete
[     3.487 ms ] IDLE start
[     7.005 ms ] IDLE pause
[     7.006 ms ] HRT_Actuator start
[    10.001 ms ] HRT_Actuator terminate (deadline miss)
[    10.009 ms ] HRT_Control start
[    13.001 ms ] HRT_Control terminate (deadline miss)
[    13.008 ms ] SRT-background start
[    17.005 ms ] SRT-background pause
[    17.007 ms ] HRT_Actuator start
[    17.493 ms ] HRT_Actuator complete
[    17.498 ms ] SRT-background start
[    20.002 ms ] SRT-background terminate (subframe overflow)
```

## Support
This project is developed as part of a university assignment.
For support or questions, please use direct communication with the project authors for academic-related questions.
For support regarding usage details, please refer to the full documentation provided within the repository.

## Authors
- Stefano Falcetta
- Cristian Sapia
- Stefano Calandrella
- Mattia Rabezzana

## License
This project is released under the **MIT License**.
See the ```LICENSE``` file in the repository for details.
