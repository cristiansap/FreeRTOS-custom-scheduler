#include "FreeRTOS.h"
#include "setup.h"
#include "task.h"

// Very short deadline

void PROFILE_setup(void)
{
    xTaskHrtCreate(prvHrtTaskSimulateWork, "HRT_A", NULL, 0, 0, 2, NULL);
    xTaskHrtCreate(prvHrtTaskSimulateWork, "HRT_B", NULL, 1, 2, 4, NULL);
    xTaskHrtCreate(prvHrtTaskSimulateWork, "HRT_C", NULL, 2, 0, 1, NULL); 
    xTaskHrtCreate(prvHrtTaskSimulateWork, "HRT_D", NULL, 3, 9, 10, NULL);

    vPrintSubframes();
}
