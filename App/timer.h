#ifndef TIMER_H
#define TIMER_H

#include <stdint.h>

#define SYSTICK_LOAD (*(volatile uint32_t*)0xE000E014)
#define SYSTICK_VAL  (*(volatile uint32_t*)0xE000E018)

//return the current CPU tick
uint64_t ullGetCpuTicks(void);

#endif