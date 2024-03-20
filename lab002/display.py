from migen import *

from tick import Tick

# Goals:
# - understand own to use external modules
# - understand seven segment display and create simple digit controller
# - understand how to multiplex displays
# - use python capabilities to create visual simulations

# SevenSegment -------------------------------------------------------------------------------------

class SevenSegment(Module):
    def __init__(self):
        # Module's interface
        self.value   = value = Signal(4)         # input
        self.abcdefg = abcdefg = Signal(7)     # output

        # # #

        # Value to abcd segments dictionary.
        # Here we create a table to translate each of the 16 possible input
        # values to abdcefg segments control.
        cases = {
          0x0: abcdefg.eq(0b0111111),
          0x1: abcdefg.eq(0b0000110),
          0x2: abcdefg.eq(0b1011011),
          0x3: abcdefg.eq(0b1001111),
          0x4: abcdefg.eq(0b1100110),
          0x5: abcdefg.eq(0b1101101),
          0x6: abcdefg.eq(0b1111101),
          0x7: abcdefg.eq(0b0000111),
          0x8: abcdefg.eq(0b1111111),
          0x9: abcdefg.eq(0b1101111),
          0xa: abcdefg.eq(0b1110111),
          0xb: abcdefg.eq(0b1111100),
          0xc: abcdefg.eq(0b1011000),
          0xd: abcdefg.eq(0b1011110),
          0xe: abcdefg.eq(0b1111001),
          0xf: abcdefg.eq(0b1110001),
        }

        # Combinatorial assignement
        self.comb += Case(value, cases)

# SevenSegmentDisplay ------------------------------------------------------------------------------

class SevenSegmentDisplay(Module):
    def __init__(self, sys_clk_freq, cs_period=0.001, digits=8):
        # Module's interface
        self.values = Array(Signal(5) for i in range(digits))  # input

        self.cs = Signal(digits) # output
        self.abcdefg = Signal(7) # output

        # # #

        # Create our seven segment controller
        seven_segment = SevenSegment()
        self.submodules += seven_segment
        self.comb += self.abcdefg.eq(seven_segment.abcdefg)

        # Create a tick every cs_period
        self.submodules.tick = Tick(sys_clk_freq, cs_period)

        # Rotate cs <digits> bits signals to alternate seven segments
        # cycle 0 : 0b..000001
        # cycle 1 : 0b..000010
        # cycle 2 : 0b..000100
        # cycle 3 : 0b..001000
        # cycle 4 : 0b..010000
        # cycle 5 : 0b..100000
        # ..
        # cycle n : 0b..000001
        cs = Signal(digits, reset=1)
        # Synchronous assigment
        self.sync += [
            If(self.tick.ce,
                # rotate cs
                cs.eq((cs << 1) | (cs == (1 << (digits - 1)))),
            )
        ]
        # Combinatorial assigment
        self.comb += self.cs.eq(cs)

        # cs to value selection.
        # Here we create a table to translate each of the <digits> cs possible values
        # to input value selection.
        cases = {
            1 << i: seven_segment.value.eq(self.values[i])
            for i in range(digits)
        }

        # Combinatorial assigment
        self.comb += Case(self.cs, cases)

# Main ---------------------------------------------------------------------------------------------

if __name__ == '__main__':
    # SevenSegment simulation
    print("SevenSegment simulation")
    dut = SevenSegment()

    def show_seven_segment(abcdefg):
        line0 = ["   ", " _ "]
        line1 = ["   ", "  |", " _ ", " _|", "|  ", "| |" , "|_ ", "|_|"]
        a = abcdefg & 0b1;
        fgb = ((abcdefg >> 1) & 0b001) | ((abcdefg >> 5) & 0b010) | ((abcdefg >> 3) & 0b100)
        edc = ((abcdefg >> 2) & 0b001) | ((abcdefg >> 2) & 0b010) | ((abcdefg >> 2) & 0b100)
        print(line0[a])
        print(line1[fgb])
        print(line1[edc])

    def dut_tb(dut):
        for i in range(16):
            yield dut.value.eq(i)
            yield
            show_seven_segment((yield dut.abcdefg))

    run_simulation(dut, dut_tb(dut), vcd_name="seven_segment.vcd")

    # SevenSegmentDisplay simulation
    print("SevenSegmentDisplay simulation")
    digits = 6
    dut = SevenSegmentDisplay(100e6, 0.000001, digits)
    def dut_tb(dut):
        for i in range(4096):
            for j in range(digits):
                yield dut.values[j].eq(i + j)
            yield

    run_simulation(dut, dut_tb(dut), vcd_name="display.vcd")
