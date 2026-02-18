#include "FreeRTOS.h"
#include "setup.h"
#include "task.h"

// Stress scheduler with one huge subframe and HRT/SRT tasks

void PROFILE_setup(void)
{
    xTaskHrtCreate(prvHrtTaskSimulateWork, "HRT-0", NULL, 0, 3, 8, NULL);
    xTaskHrtCreate(prvHrtTaskSimulateWork, "HRT-1", NULL, 0, 10, 16, NULL);
    xTaskHrtCreate(prvHrtTaskSimulateWork, "HRT-2", NULL, 0, 17, 28, NULL);
    xTaskHrtCreate(prvHrtTaskSimulateWork, "HRT-3", NULL, 0, 30, 35, NULL);

    xTaskSrtCreate(prvSrtTaskSimulateWork, "SRT-A", NULL, 0, NULL);
    xTaskSrtCreate(prvSrtTaskSimulateWork, "SRT-B", NULL, 0, NULL);
    xTaskSrtCreate(prvSrtTaskSimulateWork, "SRT-C", NULL, 0, NULL);
    xTaskSrtCreate(prvSrtTaskSimulateWork, "SRT-D", NULL, 0, NULL);

    vPrintSubframes();
}
