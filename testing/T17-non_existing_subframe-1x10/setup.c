#include "FreeRTOS.h"
#include "setup.h"
#include "task.h"
#include "printf/printf.h"

// Test scheduler with HRT/SRT tasks placed in non-existing subframes (invalid configuration)

void PROFILE_setup(void)
{
    /* Test HRT task creation */

    if (xTaskHrtCreate(prvHrtTaskSimulateWork, "HRT-0", NULL, 0, 1, 3, NULL) == pdTRUE) {
        printf("[PASS] HRT create with valid subframe\n");
    } else {
        printf("[FAIL] HRT create with valid subframe\n");
        return;
    }
    
    // Invalid subframe ID (2)
    if (xTaskHrtCreate(prvHrtTaskSimulateWork, "HRT-1", NULL, 2, 5, 7, NULL) != pdTRUE) {
        printf("[PASS] HRT create with invalid subframe\n");
    } else {
        printf("[FAIL] HRT create with invalid subframe\n");
        return;
    }

    /* Do the same with SRT tasks */
    
    if (xTaskSrtCreate(prvSrtTaskSimulateWork, "SRT-A", NULL, 0, NULL) == pdTRUE) {
        printf("[PASS] SRT create with valid subframe\n");
    } else {
        printf("[FAIL] SRT create with valid subframe\n");
        return;
    }
    
    // Invalid subframe ID (3)
    if (xTaskSrtCreate(prvSrtTaskSimulateWork, "SRT-B", NULL, 3, NULL) != pdTRUE) {
        printf("[PASS] SRT create with invalid subframe\n");
    } else {
        printf("[FAIL] SRT create with invalid subframe\n");
        return;
    }
    
    
    vPrintSubframes();
}
