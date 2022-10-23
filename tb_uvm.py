#!/usr/bin/env python

from cocotb.triggers import Join, Combine
from pyuvm import *
import random
import cocotb
import pyuvm
# All testbenches use tinyalu_utils, so store it in a central
# place and add its path to the sys path so we can import it
import sys
from pathlib import Path
sys.path.append(str(Path("..").resolve()))
# from tinyalu_utils import TinyAluBfm, Ops, alu_prediction  # noqa: E402


import cocotb
from cocotb.triggers import FallingEdge
from cocotb.queue import QueueEmpty, Queue
import enum
import logging

from pyuvm import utility_classes



logging.basicConfig(level=logging.NOTSET)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


# @enum.unique
# class Ops(enum.IntEnum):
#     """Legal ops for the TinyALU"""
#     ADD = 1
#     AND = 2
#     XOR = 3
#     MUL = 4


def alu_prediction(valid, calc, error=False):
    """Python model of the TinyALU"""
    if valid == 1 and calc == 0:
        result = 1
    elif valid == 0 and calc == 1:
        result = 2
    elif valid == 1 and calc == 1:
        result = 3
    if error:
        result = 0
    return result


# def get_int(signal):
#     try:
#         sig = int(signal.value)
#     except ValueError:
#         sig = 0
#     return sig


class TinyAluBfm(metaclass=utility_classes.Singleton):
    def __init__(self):
        self.dut = cocotb.top
        self.driver_queue = Queue(maxsize=1)
        self.cmd_mon_queue = Queue(maxsize=0)
        self.result_mon_queue = Queue(maxsize=0)

    async def calc(self, valid, calc):
        command_tuple = (valid, calc)
        await self.driver_queue.put(command_tuple)

    async def get_cmd(self):
        cmd = await self.cmd_mon_queue.get()
        return cmd

    async def get_result(self):
        result = await self.result_mon_queue.get()
        return result

    async def reset(self):
        await FallingEdge(self.dut.clk)
        self.dut.reset.value = 1
        self.dut.d.value = 0
        self.dut.init.value = 1
        self.dut.d_valid.value = 0
        await FallingEdge(self.dut.clk)
        self.dut.reset.value = 0
        self.dut.init.value = 0
        await FallingEdge(self.dut.clk)

    async def driver_bfm(self):
        await ClockCycles(dut.clk, 50)
        self.dut.calc.value = 1
        self.dut.d_valid.value = 1
        while True:
            await FallingEdge(self.dut.clk)
            # start = get_int(self.dut.)
            # done = get_int(self.dut.done)
            # if start == 0 and done == 0:
            try:
                (valid, calc) = self.driver_queue.get_nowait()
                self.dut.d_valid.value = valid
                self.dut.calc.value = calc
            except QueueEmpty:
                pass

    async def cmd_mon_bfm(self):
        prev_start = 0
        while True:
            await FallingEdge(self.dut.clk)
            cmd_tuple = (get_int(self.dut.valid),
                         get_int(self.dut.calc))
            self.cmd_mon_queue.put_nowait(cmd_tuple)

    async def result_mon_bfm(self):
        prev_done = 0
        while True:
            await FallingEdge(self.dut.clk)
            if prev_done == 0:
                crc = get_int(self.dut.crc)
                self.result_mon_queue.put_nowait(crc)
            prev_done = 1

    def start_bfm(self):
        cocotb.start_soon(self.driver_bfm())
        cocotb.start_soon(self.cmd_mon_bfm())
        cocotb.start_soon(self.result_mon_bfm())

# Sequence classes


class AluSeqItem(uvm_sequence_item):

    def __init__(self, name, valid, calc):
        super().__init__(name)
        self.valid = valid
        self.calc = calc

    # def randomize_operands(self):
    #     self.A = random.randint(0, 255)
    #     self.B = random.randint(0, 255)

    # def randomize(self):
    #     self.randomize_operands()
    #     self.op = random.choice(list(Ops))

    def __eq__(self, other):
        same = self.valid == other.valid and self.calc == other.calc
        return same

    def __str__(self):
        return f"{self.get_name()} : valid: 0x{self.valid:02x} \
        calc: 0x{self.calc:02x}"


# class RandomSeq(uvm_sequence):
#     async def body(self):
#         for op in list(Ops):
#             cmd_tr = AluSeqItem("cmd_tr", None, None, op)
#             await self.start_item(cmd_tr)
#             cmd_tr.randomize_operands()
#             await self.finish_item(cmd_tr)


class MaxSeq(uvm_sequence):
    async def body(self):
        cmd_tr = AluSeqItem("cmd_tr", 0x1, 0x1)
        await self.start_item(cmd_tr)
        await self.finish_item(cmd_tr)


class TestAllSeq(uvm_sequence):

    async def body(self):
        seqr = ConfigDB().get(None, "", "SEQR")
        # random = RandomSeq("random")
        max = MaxSeq("max")
        # await random.start(seqr)
        await max.start(seqr)


# class TestAllForkSeq(uvm_sequence):
#     async def body(self):
#         seqr = ConfigDB().get(None, "", "SEQR")
#         random = RandomSeq("random")
#         max = MaxSeq("max")
#         random_task = cocotb.fork(random.start(seqr))
#         max_task = cocotb.fork(max.start(seqr))
#         await Combine(Join(random_task), Join(max_task))

# Sequence library example


# class OpSeq(uvm_sequence):
#     def __init__(self, name, aa, bb, op):
#         super().__init__(name)
#         self.aa = aa
#         self.bb = bb
#         self.op = Ops(op)

#     async def body(self):
#         seq_item = AluSeqItem("seq_item", self.aa, self.bb,
#                               self.op)
#         await self.start_item(seq_item)
#         await self.finish_item(seq_item)
#         self.result = seq_item.result


# async def do_add(seqr, aa, bb):
#     seq = OpSeq("seq", aa, bb, Ops.ADD)
#     await seq.start(seqr)
#     return seq.result


# async def do_and(seqr, aa, bb):
#     seq = OpSeq("seq", aa, bb, Ops.AND)
#     await seq.start(seqr)
#     return seq.result


# async def do_xor(seqr, aa, bb):
#     seq = OpSeq("seq", aa, bb, Ops.XOR)
#     await seq.start(seqr)
#     return seq.result


# async def do_mul(seqr, aa, bb):
#     seq = OpSeq("seq", aa, bb, Ops.MUL)
#     await seq.start(seqr)
#     return seq.result


# class FibonacciSeq(uvm_sequence):
#     def __init__(self, name):
#         super().__init__(name)
#         self.seqr = ConfigDB().get(None, "", "SEQR")

#     async def body(self):
#         prev_num = 0
#         cur_num = 1
#         fib_list = [prev_num, cur_num]
#         for _ in range(7):
#             sum = await do_add(self.seqr, prev_num, cur_num)
#             fib_list.append(sum)
#             prev_num = cur_num
#             cur_num = sum
#         uvm_root().logger.info("Fibonacci Sequence: " + str(fib_list))
#         uvm_root().set_logging_level_hier(CRITICAL)


class Driver(uvm_driver):
    def build_phase(self):
        self.ap = uvm_analysis_port("ap", self)

    def start_of_simulation_phase(self):
        self.bfm = TinyAluBfm()

    async def launch_tb(self):
        await self.bfm.reset()
        self.bfm.start_bfm()

    async def run_phase(self):
        await self.launch_tb()
        while True:
            cmd = await self.seq_item_port.get_next_item()
            await self.bfm.calc(cmd.calc, cmd.valid)
            result = await self.bfm.get_result()
            self.ap.write(result)
            cmd.result = result
            self.seq_item_port.item_done()


class Coverage(uvm_subscriber):

    def end_of_elaboration_phase(self):
        self.cvg = set()

    def write(self, cmd):
        (_, _, op) = cmd
        self.cvg.add(op)

    def report_phase(self):
        try:
            disable_errors = ConfigDB().get(
                self, "", "DISABLE_COVERAGE_ERRORS")
        except UVMConfigItemNotFound:
            disable_errors = False
        if not disable_errors:
            if len(set(Ops) - self.cvg) > 0:
                self.logger.error(
                    f"Functional coverage error. Missed: {set(Ops)-self.cvg}")
                assert False
            else:
                self.logger.info("Covered all operations")
                assert True


class Scoreboard(uvm_component):

    def build_phase(self):
        self.cmd_fifo = uvm_tlm_analysis_fifo("cmd_fifo", self)
        self.result_fifo = uvm_tlm_analysis_fifo("result_fifo", self)
        self.cmd_get_port = uvm_get_port("cmd_get_port", self)
        self.result_get_port = uvm_get_port("result_get_port", self)
        self.cmd_export = self.cmd_fifo.analysis_export
        self.result_export = self.result_fifo.analysis_export

    def connect_phase(self):
        self.cmd_get_port.connect(self.cmd_fifo.get_export)
        self.result_get_port.connect(self.result_fifo.get_export)

    def check_phase(self):
        passed = True
        try:
            self.errors = ConfigDB().get(self, "", "CREATE_ERRORS")
        except UVMConfigItemNotFound:
            self.errors = False
        while self.result_get_port.can_get():
            _, actual_result = self.result_get_port.try_get()
            cmd_success, cmd = self.cmd_get_port.try_get()
            if not cmd_success:
                self.logger.critical(f"result {actual_result} had no command")
            else:
                (valid, calc) = cmd
                predicted_result = alu_prediction(valid, calc, self.errors)
                if predicted_result == actual_result:
                    self.logger.info(f"PASSED: 0x{valid:02x} 0x{calc:02x} ="
                                     f" 0x{actual_result:04x}")
                else:
                    self.logger.error(f"FAILED: 0x{valid:02x} 0x{calc:02x} "
                                      f"= 0x{actual_result:04x} "
                                      f"expected 0x{predicted_result:04x}")
                    passed = False
        assert passed


class Monitor(uvm_component):
    def __init__(self, name, parent, method_name):
        super().__init__(name, parent)
        self.method_name = method_name

    def build_phase(self):
        self.ap = uvm_analysis_port("ap", self)
        self.bfm = TinyAluBfm()
        self.get_method = getattr(self.bfm, self.method_name)

    async def run_phase(self):
        while True:
            datum = await self.get_method()
            self.logger.debug(f"MONITORED {datum}")
            self.ap.write(datum)


class AluEnv(uvm_env):

    def build_phase(self):
        self.seqr = uvm_sequencer("seqr", self)
        ConfigDB().set(None, "*", "SEQR", self.seqr)
        self.driver = Driver.create("driver", self)
        self.cmd_mon = Monitor("cmd_mon", self, "get_cmd")
        self.coverage = Coverage("coverage", self)
        self.scoreboard = Scoreboard("scoreboard", self)

    def connect_phase(self):
        self.driver.seq_item_port.connect(self.seqr.seq_item_export)
        self.cmd_mon.ap.connect(self.scoreboard.cmd_export)
        self.cmd_mon.ap.connect(self.coverage.analysis_export)
        self.driver.ap.connect(self.scoreboard.result_export)


@pyuvm.test()
class AluTest(uvm_test):
    """Test ALU with random and max values"""

    def build_phase(self):
        self.env = AluEnv("env", self)

    def end_of_elaboration_phase(self):
        self.test_all = TestAllSeq.create("test_all")

    async def run_phase(self):
        self.raise_objection()
        await self.test_all.start()
        self.drop_objection()


# @pyuvm.test()
# class ParallelTest(AluTest):
#     """Test ALU random and max forked"""

#     def build_phase(self):
#         uvm_factory().set_type_override_by_type(TestAllSeq, TestAllForkSeq)
#         super().build_phase()


# @pyuvm.test()
# class FibonacciTest(AluTest):
#     """Run Fibonacci program"""

#     def build_phase(self):
#         ConfigDB().set(None, "*", "DISABLE_COVERAGE_ERRORS", True)
#         uvm_factory().set_type_override_by_type(TestAllSeq, FibonacciSeq)
#         return super().build_phase()


# @pyuvm.test(expect_fail=True)
# class AluTestErrors(AluTest):
#     """Test ALU with errors on all operations"""

#     def start_of_simulation_phase(self):
#         ConfigDB().set(None, "*", "CREATE_ERRORS", True)
