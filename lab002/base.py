#!/usr/bin/env python3

from migen import *
from migen.genlib.cdc import MultiReg

from litex.build.generic_platform import *
from litex.build.xilinx import XilinxPlatform

from tick import *
from display import *
from bcd import *
from core import *

# IOs ----------------------------------------------------------------------------------------------

_io = [
    ("user_led",  0, Pins("H17"), IOStandard("LVCMOS33")),

    ("user_sw",  0, Pins("J15"), IOStandard("LVCMOS33")),

    ("user_btn_r", 0, Pins("M17"), IOStandard("LVCMOS33")),
    ("user_btn_l", 0, Pins("P17"), IOStandard("LVCMOS33")),

    ("clk100", 0, Pins("E3"), IOStandard("LVCMOS33")),

    ("cpu_reset", 0, Pins("C12"), IOStandard("LVCMOS33")),

    ("display_cs_n",  0, Pins("J17 J18 T9 J14 P14 T14 K2 U13"), IOStandard("LVCMOS33")),
    ("display_abcdefg",  0, Pins("T10 R10 K16 K13 P15 T11 L18"), IOStandard("LVCMOS33")),
    ("display_dot", 0, Pins("H15"), IOStandard("LVCMOS33")),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(XilinxPlatform):
    default_clk_name   = "clk100"
    default_clk_period = 1e9/100e6

    def __init__(self):
        XilinxPlatform.__init__(self, "xc7a100t-csg324-1", _io, toolchain="vivado")

# Design -------------------------------------------------------------------------------------------

# User button detection
class UserButtonPress(Module):
    def __init__(self, user_btn):
        self.rising = Signal()

        # # #

        _user_btn = Signal()
        _user_btn_d = Signal()

        # resynchronize user_btn
        self.specials += MultiReg(user_btn, _user_btn)
        # detect rising edge
        self.sync += [
            _user_btn_d.eq(user_btn),
            self.rising.eq(_user_btn & ~_user_btn_d)
        ]

# Create our platform (fpga interface)
platform = Platform()

# Create our main module (fpga description)
class Clock(Module):
    sys_clk_freq = int(100e6)
    def __init__(self, led, disp_cs, disp_abcdefg, disp_dot):
        # -- TO BE COMPLETED --
        # Tick generation : timebase
        self.submodules.tick = Tick(Clock.sys_clk_freq, 1)

        # SevenSegmentDisplay
        self.submodules.disp = SevenSegmentDisplay(
            Clock.sys_clk_freq,
            cs_period=(1/40),
            # cs_period=0.5,
            digits=8,
        )

        # Core : counts ss/mm/hh

        # set mm/hh

        # Binary Coded Decimal: convert ss/mm/hh to decimal values
        # self.submodules.bcd = BCD()

        # use the generated verilog file

        # combinatorial assignement
        for (i, x) in enumerate(reversed([3, 1, 4, 1, 5, 9, 2, 6])):
            self.comb += self.disp.values[i].eq(x)
        self.comb += [
            If(self.disp.cs == (1 << 7),
               disp_dot.eq(0),
            ).Else(
               disp_dot.eq(1),
            ),
            disp_abcdefg.eq(~self.disp.abcdefg),
            disp_cs.eq(~self.disp.cs),

            # Connect tick to core (core timebase)

            # Set minutes/hours

            # Convert core seconds to bcd and connect
            # to display

            # Convert core minutes to bcd and connect
            # to display

            # Convert core hours to bcd and connect
            # to display

            # Connect display to pads
        ]
        # -- TO BE COMPLETED --

        self.sync += [
            If(self.tick.ce, led.eq(~led)),
        ]

module = Clock(
    platform.request("user_led"),
    platform.request("display_cs_n"),
    platform.request("display_abcdefg"),
    platform.request("display_dot"),
)

# Build --------------------------------------------------------------------------------------------

platform.build(module)
