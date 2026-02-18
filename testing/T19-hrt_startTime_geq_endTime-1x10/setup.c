#include "FreeRTOS.h"
#include "setup.h"
#include "task.h"
#include "printf/printf.h"

// Test scheduler with HRT tasks that have start time greater than or equal to end time (invalid configuration)

void PROFILE_setup(void)
{
    // Task HRT-0: start time == end time (invalid)
    if (xTaskHrtCreate(prvHrtTaskSimulateWork, "HRT-0", NULL, 0, 2, 2, NULL) != pdTRUE) {
        printf("[PASS] HRT create with start time = end time\n");
    } else {
        printf("[FAIL] HRT create with start time = end time\n");
    }
    
    // Task HRT-1: start time > end time (invalid)
    if (xTaskHrtCreate(prvHrtTaskSimulateWork, "HRT-1", NULL, 0, 7, 5, NULL) != pdTRUE) {
        printf("[PASS] HRT create with start time > end time\n");
    } else {
        printf("[FAIL] HRT create with start time > end time\n");
    }

    // Task HRT-2: start time < end time (valid)
    if (xTaskHrtCreate(prvHrtTaskSimulateWork, "HRT-2", NULL, 0, 8, 10, NULL) == pdTRUE) {
        printf("[PASS] HRT create with start time < end time\n");
    } else {
        printf("[FAIL] HRT create with start time < end time\n");
    }

    vPrintSubframes();
}
