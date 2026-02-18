#include "timer.h"
#include "FreeRTOS.h"
#include "task.h"

uint64_t ullGetCpuTicks(void)
{
    uint32_t tick;
    uint32_t val;
    const uint32_t load = SYSTICK_LOAD;
    static uint64_t last_time;
    uint64_t time;

    // Check if SysTick is initialized
    if (load == 0) {
        return 0;
    }

    taskENTER_CRITICAL();
    {
        tick = xTaskGetTickCount();
        val  = SYSTICK_VAL;

        time = ((uint64_t)tick * (load + 1)) + ((load + 1) - val);

        // Fix: SysTick restarted but RTOS tick not yet incremented
        if (time < last_time) {
            time += (load + 1);
        }

        last_time = time;
    }
    taskEXIT_CRITICAL();

    return time;
}