APP = App
RTOS = FreeRTOS-Kernel
CONFIG = config
PROFILES = profiles
TESTS = testing

OUT := output
TEST_DIR := $(if $(TEST),$(OUT)/$(wildcard $(TESTS)/T$(TEST)*),)
PROFILE_DIR := $(OUT)$(if $(PROFILE),/$(PROFILES)/$(PROFILE))

TARGET_DIR := $(if $(TEST_DIR),$(TEST_DIR),$(PROFILE_DIR))

TARGET := $(TARGET_DIR)/image.elf
TARGET_TRACE := $(TARGET_DIR)/trace.elf

DEPS := $(OUT)/dependencies

CC = arm-none-eabi-gcc
LD = arm-none-eabi-gcc
AS = arm-none-eabi-as

CPU = -mcpu=cortex-m3
THUMB = -mthumb

RTOS_PORT = $(RTOS)/portable/GCC/ARM_CM3

CFLAGS += -ffreestanding $(CPU) $(THUMB)
CFLAGS += -Wall -Wextra -Wshadow
CFLAGS += -Wcast-qual -Wcast-align -Wincompatible-pointer-types
CFLAGS += -g3 -Os -ffunction-sections -fdata-sections
CFLAGS += -MMD -MP -MF"$(DEPS)/$(subst /,_,$(call rest,$(@:.o=.d)))" -MT $@
CFLAGS += -I$(CONFIG) -I$(APP) -I$(RTOS)/include -I$(RTOS_PORT)

LDFLAGS += -T $(APP)/linker.ld
LDFLAGS += -Xlinker --gc-sections
LDFLAGS += -nostartfiles

## FreeRTOS, App and profile C files

RTOS_SRC += list.c 
RTOS_SRC += queue.c 
RTOS_SRC += portable/MemMang/heap_4.c 
RTOS_SRC += portable/GCC/ARM_CM3/port.c 

RTOS_OBJ := $(RTOS_SRC:%.c=%.o)

APP_SRC += main.c 
APP_SRC += uart.c 
APP_SRC += printf/printf.c 
APP_SRC += timer.c

APP_OBJ := $(APP_SRC:%.c=%.o) startup.o

COMMON_OUT := $(addprefix $(OUT)/,$(APP_OBJ) $(RTOS_OBJ))

head = $(firstword $(subst /, ,$1))
rest = $(subst $(firstword $(subst /, ,$1))/,,$1)

all: $(TARGET)

.SECONDARY:

$(OUT)/%/tasks.o: $(RTOS)/tasks.c
	@mkdir -p $(dir $@) $(DEPS)
	$(CC) -I$* $(CFLAGS) -c $< -o $@

$(OUT)/%/setup.o: %/setup.c
	@mkdir -p $(dir $@) $(DEPS)
	$(CC) -I$* $(CFLAGS) -c $< -o $@

$(OUT)/tasks_trace.o: $(RTOS)/tasks.c
	@mkdir -p $(dir $@) $(DEPS)
	$(CC) -include TracingConfig.h $(CFLAGS) -c $< -o $@

$(OUT)/%/tasks_trace.o: $(RTOS)/tasks.c
	@mkdir -p $(dir $@) $(DEPS)
	$(CC) -include TracingConfig.h -I$* $(CFLAGS) -c $< -o $@

$(OUT)/%.o: $(APP)/%.s
	@mkdir -p $(dir $@) $(DEPS)
	$(AS) $(CPU) $(THUMB) $< -o $@

$(OUT)/%.o: $(APP)/%.c
	@mkdir -p $(dir $@) $(DEPS)
	$(CC) $(CFLAGS) -c $< -o $@

$(OUT)/%.o: $(RTOS)/%.c
	@mkdir -p $(dir $@) $(DEPS)
	$(CC) $(CFLAGS) -c $< -o $@

$(OUT)/image.elf: $(OUT)/tasks.o $(COMMON_OUT)
	$(LD) $(CFLAGS) $(LDFLAGS) $^ -o $@

$(OUT)/trace.elf: $(OUT)/tasks_trace.o $(COMMON_OUT)
	$(LD) $(CFLAGS) $(LDFLAGS) $^ -o $@

$(OUT)/%/image.elf: $(OUT)/%/tasks.o $(OUT)/%/setup.o $(COMMON_OUT)
	$(LD) $(CFLAGS) $(LDFLAGS) $^ -o $@

$(OUT)/%/trace.elf: $(OUT)/%/tasks_trace.o $(OUT)/%/setup.o $(COMMON_OUT)
	$(LD) $(CFLAGS) $(LDFLAGS) $^ -o $@

clean:
	@rm -rf $(OUT)

run: $(TARGET)
	qemu-system-arm -machine mps2-an385 -cpu cortex-m3 -kernel $(TARGET) -monitor none -nographic -serial stdio

debug: $(TARGET)
	python3 scripts/debug.py $(TARGET)

debug_graph: $(TARGET)
	python3 scripts/graph.py $(TARGET)

trace: $(TARGET_TRACE)
	python3 scripts/tracing.py $(TARGET_TRACE) --traces

trace_graph: $(TARGET_TRACE)
	python3 scripts/tracing.py $(TARGET_TRACE) --graph --prints

TEST_SUBDIRS := $(wildcard $(TESTS)/T*)
TEST_TARGETS := $(foreach dir,$(TEST_SUBDIRS),$(OUT)/$(dir)/trace.elf)

test: $(TEST_TARGETS)
	@python3 scripts/testing.py $^

profile:
	@python3 scripts/profile.py

-include $(wildcard $(DEPS)/**.d)

.PHONY: all clean run graph debug profile
