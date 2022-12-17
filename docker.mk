SIM ?= vcs

# Wait for free license
ifeq ($(SIM),vcs)
	PLUSARGS = +vcs+lic+wait
endif

GUI ?= 0 # Cannot be 1 while running in docker for now
WAVES ?= 1

COCOTB_REDUCED_LOG_FMT = False ## True
COCOTB_LOG_LEVEL = DEBUG

PWD=$(shell pwd)

TOPLEVEL_LANG ?= systemverilog
VERILOG_SOURCES = $(PWD)/src/crc32_8.sv

TOPLEVEL := crc32_8
MODULE	 := tb_uvm
# MODULE	 := tb_simple

SIM_BUILD ?= output
# FIXME: log both compile and sim
# EXTRA_ARGS += -sml -l $(PWD)/$$SIM_BUILD/sim.log -cm cond+tgl+line+fsm -debug_access+all -cov_text_report fifo_test.vdb
EXTRA_ARGS += -sml -l $(PWD)/$$SIM_BUILD/sim.log -cm cond+tgl+line+fsm

COCOTB_HDL_TIMEUNIT = 1ps
COCOTB_HDL_TIMEPRECISION = 1ps

include $(shell cocotb-config --makefiles)/Makefile.sim

cleanall: clean
	@rm -rf output
	@rm -rf __pycache__
	@rm -rf results.xml
	@rm -rf log.txt
	@rm -rf sim_build
	@rm -rf modelsim.ini
	@rm -rf transcript
	@rm -rf waveform.vcd
	@rm -rf DVEfiles
	@rm -rf *.vcd
	@rm -rf *.vpd
	@rm -rf ucli.key
