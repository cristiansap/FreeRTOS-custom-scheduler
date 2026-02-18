#include <printf/printf.h>
#include "timer.h"

#define traceTASK_SWITCHED_IN() \
    printf("[TRACE] %08llu TASK %s\n", ullGetCpuTicks(), pxCurrentTCB->pcTaskName);

#define traceTASK_SWITCHED_OUT() \
    printf("[TRACE] %08llu TASK_END %s\n", ullGetCpuTicks(), pxCurrentTCB->pcTaskName);

// Timing every xTaskIncrementTick is needed to determine when to stop

#define traceENTER_xTaskIncrementTick() \
    printf("[TRACE] %08llu SysTick\n", ullGetCpuTicks())

#define traceRETURN_xTaskIncrementTick(_) \
    printf("[TRACE] %08llu SysTick_END\n", ullGetCpuTicks())

#define traceENTER_vTaskSwitchContext() \
    printf("[TRACE] %08llu PendSV\n", ullGetCpuTicks())

#define traceRETURN_vTaskSwitchContext() \
    printf("[TRACE] %08llu PendSV_END\n", ullGetCpuTicks())

#define traceENTER_vTaskStartScheduler() \
    printf("[TASKS] %lu ", configSUBFRAME_DURATION); vPrintSubframesJson();

#define INCLUDE_vPrintSubframesJson 1

#define traceTASK_HRT_DEADLINE_MISS(pxTask) \
    printf("[TRACE] %08llu MISS %s\n", ullGetCpuTicks(), pxTask->pcTaskName);

#define traceTASK_SRT_OVERFLOW(pxTask) \
    printf("[TRACE] %08llu OVERFLOW %s\n", ullGetCpuTicks(), pxTask->pcTaskName);

#define traceTASK_HRT_COMPLETE(pxTask) \
    printf("[TRACE] %08llu COMPLETE %s\n", ullGetCpuTicks(), pxTask->pcTaskName);

#define traceTASK_SRT_COMPLETE(pxTask) traceTASK_HRT_COMPLETE(pxTask)
