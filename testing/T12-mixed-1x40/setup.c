#include "FreeRTOS.h"
#include "setup.h"
#include "task.h"

// Single subframe (40 ms), mixed HRT and SRT tasks

void PROFILE_setup(void)
{
    xTaskHrtCreate(prvHrtTaskSimulateWork, "HRT_1", NULL, 0, 0, 10, NULL);
    xTaskHrtCreate(prvHrtTaskSimulateWork, "HRT_2", NULL, 0, 20, 40, NULL);

    xTaskSrtCreate(prvSrtTaskSimulateWork, "SRT-1-1", NULL, 0, NULL);
    xTaskSrtCreate(prvSrtTaskSimulateWork, "SRT-1-2", NULL, 0, NULL);
    xTaskSrtCreate(prvSrtTaskSimulateWork, "SRT-1-3", NULL, 0, NULL);
    xTaskSrtCreate(prvSrtTaskSimulateWork, "SRT-1-4", NULL, 0, NULL);

    vPrintSubframes();
}
