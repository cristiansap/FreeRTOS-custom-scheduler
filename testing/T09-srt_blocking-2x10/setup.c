#include "FreeRTOS.h"
#include "setup.h"
#include "task.h"

// HRTs occupy the entire subframes (simulating infinite work) preventing SRTs execution

void PROFILE_setup(void)
{
    xTaskHrtCreate(prvHrtTaskSimulateInfiniteWork, "HRT_A1", NULL, 0, 0, 4, NULL);
    xTaskHrtCreate(prvHrtTaskSimulateInfiniteWork, "HRT_A2", NULL, 0, 4, 10, NULL);
    xTaskSrtCreate(prvSrtTaskSimulateWork, "SRT-0-1", NULL, 0, NULL);

    xTaskHrtCreate(prvHrtTaskSimulateInfiniteWork, "HRT_B1", NULL, 1, 0, 10, NULL);
    xTaskSrtCreate(prvSrtTaskSimulateWork, "SRT-1-1", NULL, 1, NULL);

    vPrintSubframes();
}
