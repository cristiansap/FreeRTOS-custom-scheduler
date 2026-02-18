#include "FreeRTOS.h"
#include "task.h"

#include <stdio.h>
#include <string.h>

#include "uart.h"
#include "printf/printf.h"
#include "timer.h"

inline void putchar_(char c) { UART_putchar(c); }

static uint32_t uxRandState = 1;

int rand(void)
{
    uxRandState = (uxRandState * 1103515245U + 12345U) & 0x7FFFFFFFU;
    return (int) (uxRandState >> 16) & 0x7FFF;
}

static StaticTask_t mainTask;
static StackType_t mainStack[256];

void SystemInit(void) {
    UART_init();
}

void main(void * _) {
    UART_print("Hello world!\n");

    vTaskDelete(NULL);
}

__attribute__((weak)) void PROFILE_setup(void) {

    xTaskCreateStatic(main, "main", 256, NULL, tskIDLE_PRIORITY + 1, mainStack, &mainTask);
}


void _start(void) {
    /* Create profile tasks */
    PROFILE_setup();

    /* Start scheduler */
    vTaskStartScheduler();

    /* Should never reach here */
    for(;;);
}

/**
 * @brief HRT task that simulates infinite work
 * @param pvParameters Pointer to HRTTask_t structure
 */
void prvHrtTaskSimulateInfiniteWork(void *pvParameters) {
    (void) pvParameters;

    TickType_t xStartTick = xTaskGetTickCount();
    HRTHandle_t pxTask = (HRTHandle_t) xTaskGetCurrentTaskHandle();

    // Busy-waiting indefinitely
    while (1) {
        /* Empty loop simulates computational work */
    }
}

/**
 * @brief Generic work simulation function for HRT tasks
 * Uses simple LCG for random duration generation
 * @param pvParameters Pointer to HRTTask_t structure
 */
void prvHrtTaskSimulateWork(void *pvParameters)
{
    (void) pvParameters;

    TickType_t xStartTick = xTaskGetTickCount();
    HRTHandle_t pxTask = (HRTHandle_t) xTaskGetCurrentTaskHandle();

    // Compute max duration
    uint32_t ulMaxDuration = pxTask->ulEndTime - pxTask->ulStartTime;
    
    // Random duration between 0 and 1.5 * max duration (to have possible deadline misses)
    uint32_t ulTickDuration = rand() % (ulMaxDuration + (ulMaxDuration >> 1));
    int64_t llRemaining = ulTickDuration * 25000 + (rand() % 25000);

    uint64_t ullPreviousTime = ullGetCpuTicks();
    while (llRemaining > 0) {
        uint64_t ullCurrentTime = ullGetCpuTicks();
        uint64_t ullDiff = ullCurrentTime - ullPreviousTime;

        if (ullDiff < 100) llRemaining -= ullDiff;
        ullPreviousTime = ullCurrentTime;
    }
}

/**
 * @brief Generic work simulation function for SRT tasks
 * @param pvParameters Pointer to HRTTask_t structure
 */
void prvSrtTaskSimulateWork(void *pvParameters)
{
    (void) pvParameters;

    TickType_t xStartTick = xTaskGetTickCount();
    HRTHandle_t pxTask = (HRTHandle_t) xTaskGetCurrentTaskHandle();

    // Use CLZ to obtain a well-distributed workload
    // logarithmic distribution (avoid uniform distribution to be more realistic)

    // rand() returns up to 15 bits, so a 32-bit value has at least 17 leading zeros
    // Subtract 17 to scale to 0..15, sum twice to reduce the chance of getting zero
    uint32_t ulTickDuration = 0;
    ulTickDuration += ucPortCountLeadingZeros(rand()) - 17;
    ulTickDuration += ucPortCountLeadingZeros(rand()) - 17;

    int64_t llRemaining = ulTickDuration * 25000 + (rand() % 25000);

    uint64_t ullPreviousTime = ullGetCpuTicks();
    while (llRemaining > 0) {
        uint64_t ullCurrentTime = ullGetCpuTicks();
        uint64_t ullDiff = ullCurrentTime - ullPreviousTime;

        if (ullDiff < 100) llRemaining -= ullDiff;
        ullPreviousTime = ullCurrentTime;
    }
}