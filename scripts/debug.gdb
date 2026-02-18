set $SysTick_CTRL_PTR = (int*) 0xE000E010
set $SysTick_LOAD_PTR = (int*) 0xE000E014
set $SysTick_VALUE_PTR = (int*) 0xE000E018

set $NVIC_INT_CTRL_PTR = (uint32_t*) 0xE000ED04

set $cpu_ticks = 0
set $old_timer_value = 0

set $initial_last_breakpoint = 6
set $last_breakpoint = $initial_last_breakpoint

define handleLateSysTick
  set $extra_ticks = *$SysTick_LOAD_PTR + 1 - *$SysTick_VALUE_PTR
  if $extra_ticks < 5000
    set $cpu_ticks = $cpu_ticks + $extra_ticks + $old_timer_value
    set $old_timer_value = *$SysTick_VALUE_PTR
    printf "[GDB] WARNING SysTick was serviced later than %u ticks!\n", $extra_ticks
  else
    printf "[GDB] FAILED to track time, %u ticks delay in SysTick.\n", $extra_ticks
    quit
  end
end

define updateCpuTicks
  if *$SysTick_VALUE_PTR == 0
    # ($cpu_ticks == 0) handles when a single task runs before the first SysTick. 
    # SysTick and PendSV never triggered immediately after the scheduler starts.
    if $old_timer_value != *$SysTick_LOAD_PTR + 1 || $cpu_ticks == 0
      set $cpu_ticks = $cpu_ticks + $old_timer_value
      set $old_timer_value = *$SysTick_LOAD_PTR + 1
    end
  else
    if *$SysTick_VALUE_PTR <= $old_timer_value
      set $cpu_ticks = $cpu_ticks + $old_timer_value - *$SysTick_VALUE_PTR
      set $old_timer_value = *$SysTick_VALUE_PTR
    else
      handleLateSysTick
    end
  end
end

watch *$SysTick_CTRL_PTR
commands
  silent
  set $old_timer_value = *$SysTick_LOAD_PTR + 1
  printf "[GDB] %08u TASK %s\n", $cpu_ticks, pxCurrentTCB->pcTaskName
  continue
end

define tasklog
  set $systick_limit = $arg0 
  continue
end

define updateReturnBreak
  if $last_breakpoint > $initial_last_breakpoint
    delete $last_breakpoint
  end
  set $last_breakpoint++
  tbreak *$arg0 
  commands
    silent
    updateCpuTicks
    printf "[GDB] %08u TASK %s\n", $cpu_ticks, pxCurrentTCB->pcTaskName
    continue
  end
end

break xPortStartScheduler
commands
  silent
  printf "[GDB] STARTED FreeRTOS scheduler!\n"
  watch pxCurrentTCB->pxTopOfStack
  commands
    silent
    updateReturnBreak pxCurrentTCB->pxTopOfStack[14]
    continue
  end
  continue
end

watch *$NVIC_INT_CTRL_PTR
commands
  silent
  updateCpuTicks
  if *$NVIC_INT_CTRL_PTR & 0x10000000
    printf "[GDB] %08u PENDSVSET\n", $cpu_ticks
  end
  continue
end

break xPortPendSVHandler
commands
  silent
  updateCpuTicks
  printf "[GDB] %08u PendSV\n", $cpu_ticks
  set $interrupted_task = ((uint32_t *) $psp)[6]
  updateReturnBreak $interrupted_task
  continue
end

break xPortSysTickHandler
commands
  silent
  updateCpuTicks
  printf "[GDB] %08u SysTick\n", $cpu_ticks
  set $interrupted_task = ((uint32_t *) $psp)[6]
  updateReturnBreak $interrupted_task
  
  if $cpu_ticks >= $systick_limit * (*$SysTick_LOAD_PTR +1)
    printf "[GDB] COMPLETED simulation time.\n"
    quit
  else
    continue
  end
end
