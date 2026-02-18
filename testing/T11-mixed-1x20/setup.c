#include "FreeRTOS.h"
#include "setup.h"
#include "task.h"

// Single subframe (20 ms); mixed HRT and SRT tasks

void PROFILE_setup(void)
{
    xTaskHrtCreate(prvHrtTaskSimulateWork, "HRT_1", NULL, 0, 5, 10, NULL);
    xTaskHrtCreate(prvHrtTaskSimulateWork, "HRT_2", NULL, 0, 10, 15, NULL);

    xTaskSrtCreate(prvSrtTaskSimulateWork, "SRT-0-1", NULL, 0, NULL);
    xTaskSrtCreate(prvSrtTaskSimulateWork, "SRT-0-2", NULL, 0, NULL);
    xTaskSrtCreate(prvSrtTaskSimulateWork, "SRT-0-3", NULL, 0, NULL);
    xTaskSrtCreate(prvSrtTaskSimulateWork, "SRT-0-4", NULL, 0, NULL);

    vPrintSubframes();
}
