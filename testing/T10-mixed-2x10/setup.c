#include "FreeRTOS.h"
#include "setup.h"
#include "task.h"

// Mixed scheduling with HRT and SRT tasks

void PROFILE_setup(void)
{
    xTaskHrtCreate(prvHrtTaskSimulateWork, "HRT_A1", NULL, 0, 2, 4, NULL);
    xTaskHrtCreate(prvHrtTaskSimulateWork, "HRT_A2", NULL, 0, 6, 8, NULL);
    xTaskSrtCreate(prvSrtTaskSimulateWork, "SRT-0-1", NULL, 0, NULL);
    xTaskSrtCreate(prvSrtTaskSimulateWork, "SRT-0-2", NULL, 0, NULL);
    xTaskSrtCreate(prvSrtTaskSimulateWork, "SRT-0-3", NULL, 0, NULL);
    xTaskSrtCreate(prvSrtTaskSimulateWork, "SRT-0-4", NULL, 0, NULL);

    xTaskHrtCreate(prvHrtTaskSimulateWork, "HRT_B1", NULL, 1, 1, 5, NULL);
    xTaskHrtCreate(prvHrtTaskSimulateWork, "HRT_B2", NULL, 1, 6, 10, NULL);
    xTaskSrtCreate(prvSrtTaskSimulateWork, "SRT-1-1", NULL, 1, NULL);

    vPrintSubframes();
}
