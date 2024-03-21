#!/usr/bin/env python3

from datetime import datetime, timedelta

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

    # ("display_cs_n",  0, Pins("T9 J14 P14 T14 K2 U13"), IOStandard("LVCMOS33")),
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
        self.submodules.tick = Tick(Clock.sys_clk_freq, 0.01)

        # SevenSegmentDisplay
        self.submodules.disp = SevenSegmentDisplay(
            Clock.sys_clk_freq,
            # cs_period=(1/40),
            # cs_period=0.5,
            digits=8,
        )

        # Core : counts ss/mm/hh
        now = datetime.now() + timedelta(seconds=42)
        self.submodules.core = Core(
            # set mm/hh
            hours=now.hour,
            minutes=now.minute,
            seconds=now.second,
        )

        # Binary Coded Decimal: convert ss/mm/hh to decimal values
        self.submodules.hours = BCD()
        self.submodules.minutes = BCD()
        self.submodules.seconds = BCD()
        # self.submodules.centis = BCD()

        # use the generated verilog file
        # no.

        # combinatorial assignement
        self.comb += [

            # Connect tick to core (core timebase)
            self.core.tick.eq(self.tick.ce),

            # Set minutes/hours
            # ?

#             # Convert core seconds to bcd and connect
#             # to display
#             self.centis.value.eq(self.core.centis),
#             self.disp.values[0].eq(self.centis.ones),
#             self.disp.values[1].eq(self.centis.tens),

            # Convert core seconds to bcd and connect
            # to display
            self.seconds.value.eq(self.core.seconds),
            self.disp.values[0].eq(self.seconds.ones),
            self.disp.values[1].eq(self.seconds.tens),

            # Convert core minutes to bcd and connect
            # to display
            self.minutes.value.eq(self.core.minutes),
            self.disp.values[3].eq(self.minutes.ones),
            self.disp.values[4].eq(self.minutes.tens),

            # Convert core hours to bcd and connect
            # to display
            self.hours.value.eq(self.core.hours),
            self.disp.values[6].eq(self.hours.ones),
            self.disp.values[7].eq(self.hours.tens),

            # Connect display to pads
            # disp_abcdefg.eq(~self.disp.abcdefg),

            Case(self.disp.cs, {
                # Empty digits
                1 << 2: disp_abcdefg.eq(0b11111111),
                1 << 5: disp_abcdefg.eq(0b11111111),
                "default": disp_abcdefg.eq(~self.disp.abcdefg),
            }),

            disp_cs.eq(~self.disp.cs),

            # Display dots to separate hours, minutes,
            # and seconds.
            disp_dot.eq(1),

#             Case(self.disp.cs, {
#                 1 << 6: disp_dot.eq(0),
#                 1 << 4: disp_dot.eq(0),
#                 1 << 2: disp_dot.eq(0),
#                 "default": disp_dot.eq(1),
#             }),

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
