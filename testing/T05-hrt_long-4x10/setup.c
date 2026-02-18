#include "FreeRTOS.h"
#include "setup.h"
#include "task.h"

// Tasks occupy (almost) the full subframe duration

void PROFILE_setup(void)
{
    xTaskHrtCreate(prvHrtTaskSimulateWork, "HRT_A", NULL, 0, 0, 10, NULL);
    xTaskHrtCreate(prvHrtTaskSimulateWork, "HRT_B", NULL, 1, 1, 8, NULL);
    xTaskHrtCreate(prvHrtTaskSimulateWork, "HRT_C", NULL, 2, 2, 9, NULL);
    xTaskHrtCreate(prvHrtTaskSimulateWork, "HRT_D", NULL, 3, 1, 10, NULL);

    vPrintSubframes();
}
