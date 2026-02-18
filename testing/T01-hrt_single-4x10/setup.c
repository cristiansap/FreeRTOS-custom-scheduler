#include "FreeRTOS.h"
#include "setup.h"
#include "task.h"

// Minimum HRT case (one per subframe); correct start/end check

void PROFILE_setup(void)
{
    xTaskHrtCreate(prvHrtTaskSimulateWork, "HRT_0", NULL, 0, 0, 5, NULL);
    xTaskHrtCreate(prvHrtTaskSimulateWork, "HRT_1", NULL, 1, 6, 10, NULL);
    xTaskHrtCreate(prvHrtTaskSimulateWork, "HRT_2", NULL, 2, 1, 9, NULL);
    xTaskHrtCreate(prvHrtTaskSimulateWork, "HRT_3", NULL, 3, 0, 10, NULL);

    vPrintSubframes();
}
