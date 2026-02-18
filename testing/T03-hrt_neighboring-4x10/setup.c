#include "FreeRTOS.h"
#include "setup.h"
#include "task.h"

// Check: exact boundaries, no overlap, correct restart

void PROFILE_setup(void)
{
    xTaskHrtCreate(prvHrtTaskSimulateWork, "HRT_0", NULL, 0, 8, 10, NULL);
    
    xTaskHrtCreate(prvHrtTaskSimulateWork, "HRT_1", NULL, 1, 0, 5, NULL);

    xTaskHrtCreate(prvHrtTaskSimulateWork, "HRT_2-1", NULL, 2, 2, 5, NULL);
    xTaskHrtCreate(prvHrtTaskSimulateWork, "HRT_2-2", NULL, 2, 5, 10, NULL);

    xTaskHrtCreate(prvHrtTaskSimulateWork, "HRT_3-1", NULL, 3, 0, 5, NULL);
    xTaskHrtCreate(prvHrtTaskSimulateWork, "HRT_3-2", NULL, 3, 5, 10, NULL);

    vPrintSubframes();
}
