#!/usr/bin/env python3

from migen import *

from litex.build.generic_platform import *
from litex.build.xilinx import XilinxPlatform

# IOs ----------------------------------------------------------------------------------------------

_io = [
    ("user_led",  0, Pins("H17"), IOStandard("LVCMOS33")),

    ("user_sw",  0, Pins("J15"), IOStandard("LVCMOS33")),

    ("user_btn", 0, Pins("N17"), IOStandard("LVCMOS33")),

    ("clk100", 0, Pins("E3"), IOStandard("LVCMOS33")),

    ("cpu_reset", 0, Pins("C12"), IOStandard("LVCMOS33")),

    ("rgb_r", 0, Pins("N16"), IOStandard("LVCMOS33")),
    ("rgb_g", 0, Pins("R11"), IOStandard("LVCMOS33")),
    ("rgb_b", 0, Pins("G14"), IOStandard("LVCMOS33")),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(XilinxPlatform):
    default_clk_name   = "clk100"
    default_clk_period = 1e9/100e6

    def __init__(self):
        XilinxPlatform.__init__(self, "xc7a100t-csg324-1", _io, toolchain="vivado")

# Design -------------------------------------------------------------------------------------------

# Create our platform (fpga interface)
platform = Platform()
led = platform.request("user_led")
rgb_r = platform.request("rgb_r")
rgb_g = platform.request("rgb_g")
rgb_b = platform.request("rgb_b")

# Create our module (fpga description)
module = Module()

# Create a counter and blink a led
counter = Signal(27)
quarter_seconds = Signal(3)
pwm = Signal(4)
module.comb += [
    led.eq(quarter_seconds[2]),
    rgb_r.eq(quarter_seconds[2] & (pwm == 0)),
    rgb_g.eq(quarter_seconds[1] & (pwm == 0)),
    rgb_b.eq(quarter_seconds[0] & (pwm == 0)),
]
module.sync += [
    If(counter == 25_000_000,
        quarter_seconds.eq(quarter_seconds + 1),
        counter.eq(0),
        ).Else(counter.eq(counter + 1)),
    pwm.eq(pwm + 1),
]

# Build --------------------------------------------------------------------------------------------

if __name__ == '__main__':
    platform.build(module)
