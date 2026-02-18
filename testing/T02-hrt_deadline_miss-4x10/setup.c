#include "FreeRTOS.h"
#include "setup.h"
#include "task.h"

// Tasks that simulates infinite work to cause deadline misses

void PROFILE_setup(void)
{
    xTaskHrtCreate(prvHrtTaskSimulateInfiniteWork, "HRT_0", NULL, 0, 0, 5, NULL);
    xTaskHrtCreate(prvHrtTaskSimulateInfiniteWork, "HRT_1", NULL, 1, 6, 10, NULL);
    xTaskHrtCreate(prvHrtTaskSimulateInfiniteWork, "HRT_2", NULL, 2, 1, 9, NULL);
    xTaskHrtCreate(prvHrtTaskSimulateInfiniteWork, "HRT_3", NULL, 3, 0, 10, NULL);

    vPrintSubframes();
}
