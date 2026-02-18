#include "FreeRTOS.h"
#include "setup.h"
#include "task.h"

#include "printf/printf.h"

#define sprintf sprintf_

// Stress scheduler with short subframes and HRT/SRT tasks in each subframe

void PROFILE_setup(void)
{
    char buffer[16];

    for (int i = 0; i < configSUBFRAME_COUNT_PER_MAJOR; i++) {
        sprintf(buffer, "HRT-0%lu", i);
        xTaskHrtCreate(prvHrtTaskSimulateWork, buffer, NULL, i, 0, 2, NULL);
        sprintf(buffer, "HRT-1%lu", i);
        xTaskHrtCreate(prvHrtTaskSimulateWork, buffer, NULL, i, 4, 5, NULL);

        sprintf(buffer, "SRT-A%lu", i);
        xTaskSrtCreate(prvSrtTaskSimulateWork, buffer, NULL, i, NULL);
        sprintf(buffer, "SRT-B%lu", i);
        xTaskSrtCreate(prvSrtTaskSimulateWork, buffer, NULL, i, NULL);
    }

    vPrintSubframes();
}