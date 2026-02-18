#include "FreeRTOS.h"
#include "setup.h"
#include "task.h"

// Only SRT tasks to show best-effort behavior while matching the fixed compile-time order

void PROFILE_setup(void)
{
    xTaskSrtCreate(prvSrtTaskSimulateWork,"SRT_A", NULL, 0, NULL);

    xTaskSrtCreate(prvSrtTaskSimulateWork,"SRT_B1", NULL, 1, NULL);
    xTaskSrtCreate(prvSrtTaskSimulateWork,"SRT_B2", NULL, 1, NULL);

    xTaskSrtCreate(prvSrtTaskSimulateWork,"SRT_C1", NULL, 2, NULL);
    xTaskSrtCreate(prvSrtTaskSimulateWork,"SRT_C2", NULL, 2, NULL);
    xTaskSrtCreate(prvSrtTaskSimulateWork,"SRT_C3", NULL, 2, NULL);

    vPrintSubframes();
}
