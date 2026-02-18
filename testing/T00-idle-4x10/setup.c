#include "FreeRTOS.h"
#include "setup.h"
#include "task.h"


// Make sure the scheduler starts even without tasks

void PROFILE_setup(void)
{
    /* No tasks */
    vPrintSubframes();
}
