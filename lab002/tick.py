from migen import *

# Goals:
# - understand Migen's Modules/IOs
# - understand Migen's syntax
# - simulate a module

# Tick ---------------------------------------------------------------------------------------------

class Tick(Module):
    def __init__(self, sys_clk_freq, period):
        # Module's interface
        self.enable = Signal(reset=1) # input
        self.ce     = Signal()        # output

        # # #

        counter_preload = int(period*sys_clk_freq - 1)
        counter = Signal(max=counter_preload)
        # counter = Signal(max=int(period*sys_clk_freq - 1))

        # Combinatorial assignements
        self.comb += self.ce.eq(counter == 0)

        # Synchronous assignments
        self.sync += [
            If(~self.enable | self.ce,
                counter.eq(counter_preload)
            ).Else(
                counter.eq(counter - 1)
            )
        ]


class Pulse(Module):
    def __init__(self, sys_clk_freq, high_width, low_width):
        self.ce = Signal() # output

        # # #

        high_width = int(high_width*sys_clk_freq)
        low_width = int(low_width*sys_clk_freq)
        counter = Signal(max=low_width + high_width)

        self.sync += [
            If(self.ce,
               If(counter == low_width + high_width,
                  self.ce.eq(0),
                  counter.eq(0),
               ).Else(counter.eq(counter + 1)),
            ).Else(
                counter.eq(counter + 1),
                If(counter == low_width,
                   self.ce.eq(1),
                ),
            ),
        ]

# Main ---------------------------------------------------------------------------------------------

if __name__ == '__main__':
    dut = Tick(100e6, 1e-6)

    def dut_tb(dut):
        yield dut.enable.eq(1)
        for i in range(1024):
            yield

    run_simulation(dut, dut_tb(dut), vcd_name="tick.vcd")
