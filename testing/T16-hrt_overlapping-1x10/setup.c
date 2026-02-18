#include "FreeRTOS.h"
#include "setup.h"
#include "task.h"
#include "printf/printf.h"

// Test scheduler with overlapping HRT tasks in the following 4 overlapping configurations:
// 1. LEFT overlap (task starts before and ends during the base task)
// 2. CENTER overlap (task starts and ends during the base task)
// 3. RIGHT overlap (task starts during and ends after the base task)
// 4. WRAP overlap (task starts before and ends after the base task)

// Note: The HRT-BASE task is created first, and it is valid.

void PROFILE_setup(void)
{
    if (xTaskHrtCreate(prvHrtTaskSimulateWork, "HRT-BASE", NULL, 0, 2, 5, NULL) == pdTRUE) {
        printf("[PASS] HRT-BASE create with valid times\n");
    } else {
        printf("[FAIL] HRT-BASE create with valid times\n");
        return;
    }

    if (xTaskHrtCreate(prvHrtTaskSimulateWork, "HRT-LEFT", NULL, 0, 1, 3, NULL) != pdTRUE) {
        printf("[PASS] HRT-LEFT create with overlapping times\n");
    } else {
        printf("[FAIL] HRT-LEFT create with overlapping times\n");
        return;
    }

    if (xTaskHrtCreate(prvHrtTaskSimulateWork, "HRT-CENTER", NULL, 0, 3, 4, NULL) != pdTRUE) {
        printf("[PASS] HRT-CENTER create with overlapping times\n");
    } else {
        printf("[FAIL] HRT-CENTER create with overlapping times\n");
        return;
    }

    if (xTaskHrtCreate(prvHrtTaskSimulateWork, "HRT-RIGHT", NULL, 0, 4, 7, NULL) != pdTRUE) {
        printf("[PASS] HRT-RIGHT create with overlapping times\n");
    } else {
        printf("[FAIL] HRT-RIGHT create with overlapping times\n");
        return;
    }

    if (xTaskHrtCreate(prvHrtTaskSimulateWork, "HRT-WRAP", NULL, 0, 1, 8, NULL) != pdTRUE) {
        printf("[PASS] HRT-WRAP create with overlapping times\n");
    } else {
        printf("[FAIL] HRT-WRAP create with overlapping times\n");
        return;
    }

    vPrintSubframes();
}
