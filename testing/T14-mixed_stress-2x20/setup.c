#include "FreeRTOS.h"
#include "setup.h"
#include "task.h"

// Stress scheduler with long subframes and HRT/SRT tasks in each subframe

void PROFILE_setup(void)
{
    xTaskHrtCreate(prvHrtTaskSimulateWork, "HRT-0-1", NULL, 0, 0, 2, NULL);
    xTaskHrtCreate(prvHrtTaskSimulateWork, "HRT-0-2", NULL, 0, 7, 9, NULL);
    xTaskHrtCreate(prvHrtTaskSimulateWork, "HRT-0-3", NULL, 0, 12, 15, NULL);

    xTaskSrtCreate(prvSrtTaskSimulateWork, "SRT-0-A", NULL, 0, NULL);
    xTaskSrtCreate(prvSrtTaskSimulateWork, "SRT-0-B", NULL, 0, NULL);
    xTaskSrtCreate(prvSrtTaskSimulateWork, "SRT-0-C", NULL, 0, NULL);

    xTaskHrtCreate(prvHrtTaskSimulateWork, "HRT-1-1", NULL, 1, 1, 8, NULL);
    xTaskHrtCreate(prvHrtTaskSimulateWork, "HRT-1-2", NULL, 1, 16, 18, NULL);

    xTaskSrtCreate(prvSrtTaskSimulateWork, "SRT-1-A", NULL, 1, NULL);
    xTaskSrtCreate(prvSrtTaskSimulateWork, "SRT-1-B", NULL, 1, NULL);
    xTaskSrtCreate(prvSrtTaskSimulateWork, "SRT-1-C", NULL, 1, NULL);

    vPrintSubframes();
}
