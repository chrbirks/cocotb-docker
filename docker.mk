SIM ?= vcs
ifeq ($(SIM),vcs)
	PLUSARGS = +vcs+lic+wait
endif

GUI ?= 1 # Cannot be 1 while running in docker
WAVES ?= 1

COCOTB_REDUCED_LOG_FMT = 0
COCOTB_LOG_LEVEL = DEBUG

PWD=$(shell pwd)

TOPLEVEL_LANG ?= verilog
VERILOG_SOURCES = $(PWD)/src/crc32_8.sv

TOPLEVEL := crc32_8
MODULE	 := tb

SIM_BUILD ?= output
# FIXME: log both compile and sim
EXTRA_ARGS += -sml -l $(PWD)/$$SIM_BUILD/sim.log

COCOTB_HDL_TIMEUNIT = 1ps
COCOTB_HDL_TIMEPRECISION = 1ps

include $(shell cocotb-config --makefiles)/Makefile.sim
include cleanall.mk
