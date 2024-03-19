#!/usr/bin/env python3

from migen import *

from litex.build.generic_platform import *
from litex.build.xilinx import XilinxPlatform

# IOs ----------------------------------------------------------------------------------------------

_leds = [
    "H17",
    "K15",
    "J13",
    "N14",
    "R18",
    "V17",
    "U17",
    "U16",
    "V16",
    "T15",
    "U14",
    "T16",
    "V15",
    "V14",
    "V12",
    "V11",
]

_switches = [
    "J15",
    "L16",
    "M13",
    "R15",
    "R17",
    "T18",
    "U18",
    "R13",
    "T8",
    "U8",
    "R16",
    "T13",
    "H6",
    "U12",
    "U11",
    "V10",
]

_io = {
    "user_btn": "N17",
    "clk100": "E3",
    "cpu_reset": "C12",
    "rgb_r": "N16",
    "rgb_g": "R11",
    "rgb_b": "G14",
}

_io = [(n, 0, p) for (n, p) in _io.items()] +\
        [("user_led", i, p) for (i, p) in enumerate(_leds)] +\
        [("user_sw", i, p) for (i, p) in enumerate(_switches)]

_io = [(n, i, Pins(p), IOStandard("LVCMOS33")) for (n, i, p) in _io]

# Platform -----------------------------------------------------------------------------------------

class Platform(XilinxPlatform):
    default_clk_name   = "clk100"
    default_clk_period = 1e9/100e6

    def __init__(self):
        XilinxPlatform.__init__(self, "xc7a100t-csg324-1", _io, toolchain="vivado")

# Design -------------------------------------------------------------------------------------------

# Create our platform (fpga interface)
platform = Platform()
rgb_r = platform.request("rgb_r")
rgb_g = platform.request("rgb_g")
rgb_b = platform.request("rgb_b")

# Create our module (fpga description)
module = Module()

# Create a counter and blink a led
counter = Signal(27)
quarter_seconds = Signal(3)
pwm = Signal(4)
for i in range(16):
    led = platform.request("user_led", i)
    switch = platform.request("user_sw", i)
    module.comb += led.eq(~switch if i < 8 else switch)
module.comb += [
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
