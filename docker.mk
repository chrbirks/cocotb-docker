SIM ?= vcs
GUI ?= 1 # Cannot be 1 while running in docker
WAVES ?= 1

PWD=$(shell pwd)

TOPLEVEL_LANG ?= verilog
VERILOG_SOURCES = $(PWD)/src/crc32_8.sv

TOPLEVEL := crc32_8
MODULE	 := tb

SIM_BUILD ?= output

COCOTB_HDL_TIMEUNIT = 1ps
COCOTB_HDL_TIMEPRECISION = 1ps

include $(shell cocotb-config --makefiles)/Makefile.sim
include cleanall.mk
