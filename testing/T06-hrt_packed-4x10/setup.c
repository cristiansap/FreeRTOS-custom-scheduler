#include "FreeRTOS.h"
#include "setup.h"
#include "task.h"

// Tightly-packed HRTs inside each subframe

void PROFILE_setup(void)
{
    xTaskHrtCreate(prvHrtTaskSimulateWork, "HRT_A1", NULL, 0, 0, 3, NULL);
    xTaskHrtCreate(prvHrtTaskSimulateWork, "HRT_A2", NULL, 0, 3, 6, NULL);
    xTaskHrtCreate(prvHrtTaskSimulateWork, "HRT_A3", NULL, 0, 6, 10, NULL);

    xTaskHrtCreate(prvHrtTaskSimulateWork, "HRT_B1", NULL, 1, 0, 5, NULL);
    xTaskHrtCreate(prvHrtTaskSimulateWork, "HRT_B2", NULL, 1, 5, 10, NULL);

    xTaskHrtCreate(prvHrtTaskSimulateWork, "HRT_C1", NULL, 2, 0, 1, NULL);
    xTaskHrtCreate(prvHrtTaskSimulateWork, "HRT_C2", NULL, 2, 1, 10, NULL);

    xTaskHrtCreate(prvHrtTaskSimulateWork, "HRT_D1", NULL, 3, 0, 2, NULL);
    xTaskHrtCreate(prvHrtTaskSimulateWork, "HRT_D2", NULL, 3, 2, 4, NULL);
    xTaskHrtCreate(prvHrtTaskSimulateWork, "HRT_D3", NULL, 3, 4, 6, NULL);
    xTaskHrtCreate(prvHrtTaskSimulateWork, "HRT_D4", NULL, 3, 6, 8, NULL);
    xTaskHrtCreate(prvHrtTaskSimulateWork, "HRT_D5", NULL, 3, 8, 10, NULL);

    vPrintSubframes();
}
