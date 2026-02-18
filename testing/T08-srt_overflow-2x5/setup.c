#include "FreeRTOS.h"
#include "setup.h"
#include "task.h"

// Subframe duration not large enough to run all SRT tasks

void PROFILE_setup(void)
{
    xTaskSrtCreate(prvSrtTaskSimulateWork, "SRT-0-1", NULL, 0, NULL);
    xTaskSrtCreate(prvSrtTaskSimulateWork, "SRT-0-2", NULL, 0, NULL);
    xTaskSrtCreate(prvSrtTaskSimulateWork, "SRT-0-3", NULL, 0, NULL);
    xTaskSrtCreate(prvSrtTaskSimulateWork, "SRT-0-4", NULL, 0, NULL);
    xTaskSrtCreate(prvSrtTaskSimulateWork, "SRT-0-5", NULL, 0, NULL);
    xTaskSrtCreate(prvSrtTaskSimulateWork, "SRT-0-6", NULL, 0, NULL);

    xTaskSrtCreate(prvSrtTaskSimulateWork, "SRT-1-1", NULL, 1, NULL);

    vPrintSubframes();
}
