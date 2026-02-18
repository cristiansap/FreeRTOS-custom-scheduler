#include "FreeRTOS.h"
#include "setup.h"
#include "task.h"
#include "printf/printf.h"

// Test scheduler with HRT tasks that overlap the end of a subframe (but do not overlap each other)

void PROFILE_setup(void)
{
    // HRT-0 overlaps the end of subframe 0 and the start of subframe 1
    if (xTaskHrtCreate(prvHrtTaskSimulateWork, "HRT-0", NULL, 0, 8, 15, NULL) != pdTRUE) {
        printf("[PASS] HRT create with end time AFTER subframe\n");
    } else {
        printf("[FAIL] HRT create with end time AFTER subframe\n");
        return;
    }
    
    if (xTaskHrtCreate(prvHrtTaskSimulateWork, "HRT-1", NULL, 1, 6, 10, NULL) == pdTRUE) {
        printf("[PASS] HRT create with end time WITHIN subframe\n");
    } else {
        printf("[FAIL] HRT create with end time WITHIN subframe\n");
        return;
    }

    vPrintSubframes();
}
