#!/usr/bin/env python

# import random
# from crc32_8_ref import crc32_8_ref
import cocotb
from cocotb.triggers import Timer
from cocotb.triggers import FallingEdge
from cocotb.triggers import RisingEdge
from cocotb.clock import Clock
from cocotb.queue import QueueEmpty, Queue


class TinyAluBfm:
    def __init__(self, dut):
        self.dut = dut
        self.driver_queue = Queue(maxsize=1)
        self.cmd_mon_queue = Queue(maxsize=0)
        self.result_mon_queue = Queue(maxsize=0)

    async def send_op(self, aa, bb, op):
        await self.driver_queue.put((aa, bb, op))

    async def get_cmd(self):
        cmd = await self.cmd_mon_queue.get()
        return cmd

    async def get_result(self):
        result = await self.result_mon_queue.get()
        return result

    async def reset(self):
        await FallingEdge(self.dut.clk)
        self.dut.reset_n <= 0
        self.dut.A <= 0
        self.dut.B <= 0
        self.dut.op <= 0
        await FallingEdge(self.dut.clk)
        self.dut.reset_n <= 1
        await FallingEdge(self.dut.clk)

    async def driver_bfm(self):
        self.dut.start <= 0
        self.dut.A <= 0
        self.dut.B <= 0
        self.dut.op <= 0
        while True:
            await FallingEdge(self.dut.clk)
            if self.dut.start.value == 0 and self.dut.done.value == 0:
                try:
                    (aa, bb, op) = self.driver_queue.get_nowait()
                    self.dut.A = aa
                    self.dut.B = bb
                    self.dut.op = op
                    self.dut.start = 1
                except QueueEmpty:
                    pass
            elif self.dut.start == 1:
                if self.dut.done.value == 1:
                    self.dut.start = 0

    async def cmd_mon_bfm(self):
        prev_start = 0
        while True:
            await FallingEdge(self.dut.clk)
            try:
                start = int(self.dut.start.value)
            except ValueError:
                start = 0
            if start == 1 and prev_start == 0:
                self.cmd_mon_queue.put_nowait((int(self.dut.A),
                                               int(self.dut.B),
                                               int(self.dut.op)))
            prev_start = start

    async def result_mon_bfm(self):
        prev_done = 0
        while True:
            await FallingEdge(self.dut.clk)
            try:
                done = int(self.dut.done)
            except ValueError:
                done = 0

            if done == 1 and prev_done == 0:
                result = int(self.dut.result)
                self.result_mon_queue.put_nowait(result)
            prev_done = done

    async def startup_bfms(self):
        await self.reset()
        cocotb.fork(self.driver_bfm())
        cocotb.fork(self.cmd_mon_bfm())
        cocotb.fork(self.result_mon_bfm())


# class CrcEnv(uvm_env):
#     def build_phase(self):
#         self.seqr = uvm_sequencer("seqr", self)
#         ConfigDB().set(None, "*", "SEQR", self.seqr)
#         self.driver = Driver.create("driver", self)
#         self.cmd_mon = Monitor("cmd_mon", self, "get_cmd")
#         self.coverage = Coverage("coverage", self)
#         self.scoreboard = Scoreboard("scoreboard", self)

#     def connect_phase(self):
#         self.driver.seq_item_port.connect(self.seqr.seq_item_export)
#         self.cmd_mon.ap.connect(self.scoreboard.cmd_export)
#         self.cmd_mon.ap.connect(self.coverage.analysis_export)
#         self.driver.ap.connect(self.scoreboard.result_export)


# @pyuvm.test()
# class UvmTest(uvm_test):
#     """xxx"""

#     def build_phase(self):
#         self.env = CrcEnv("env", self)

#     def end_of_elaboration_phase(self):
#         self.test_all = TestAllSeq.create("test_all")

#         async def run_phase(self):
#             self.raise_objection()
#             await self.test_all.start()
#             self.drop_objection()


# @pyuvm.test()
# class BasicUvmTest(UvmTest.class_):
#     """"""

#     def build_phase(self):
#         uvm_factory().set_type_override_by_type(TestAllSeq, TestAllForkSeq)
#         super().build_phase()


@cocotb.test()
async def basic_test(dut):
    """Calc a single CRC checksum and verify it"""

    # Initial values
    dut.calc.value <= 0
    dut.d.value <= 0
    dut.d_valid.value <= 0
    dut.init.value <= 0
    dut.reset.value <= 0

    # Clock and reset
    clk = Clock(dut.clk, 3, units="ns")
    cocotb.start_soon(clk.start())

    dut.reset.value = 1
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.reset.value = 0
    await RisingEdge(dut.clk)

    await Timer(10, units="ns")
    await RisingEdge(dut.clk)

    dut.init.value = 1
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.init.value = 0

    # Start test
    dut.d.value = int("ab", base=16)
    dut.d_valid.value = 1
    dut.calc.value = 1
    await RisingEdge(dut.clk)

    await Timer(1, units="ps") # FIXME: Delta cycle problem if no wait statement here

    # assert dut.crc_reg.value == 10, f"Value is incorrect: {int(dut.crc_reg.value)} != 10"
    assert int(dut.crc_reg.value) == int("1213636406"), f"Value is incorrect: {int(dut.crc_reg.value)} != 10"

    # Run a bit for easier waveform viewing
    await Timer(10, units="ns")


if __name__ == "__main__":
    basic_test()
