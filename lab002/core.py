from functools import cache

from migen import *

# Goals:
# - understand how to create simple logical core
# - understand how to create a FSM

# Indications:
# You can choose to code the clock core with only
# - If/Elif/Else in Migen:
# https://m-labs.hk/migen/manual/fhdl.html#statements
#
# or with
#
# - a FSM in Migen:
# https://github.com/m-labs/migen/blob/master/examples/basic/fsm.py
#
# or try both...

# Core ---------------------------------------------------------------------------------------------

class Core(Module):
    def __init__(self, hours=0, minutes=0, seconds=0):
        # Module's interface
        self.tick = Signal() # input
        self.seconds = Signal(6, reset=seconds) # output
        self.minutes = Signal(6, reset=minutes) # output
        self.hours   = Signal(5, reset=hours)   # output

        # Inputs to edit time
        self.inc_minutes = Signal()
        self.dec_minutes = Signal()
        self.inc_hours = Signal()
        self.dec_hours = Signal()

        # # #

        @cache
        def delta(unit, d):
            (rollover, carry) = {
                self.hours: (24, None),
                self.minutes: (60, self.hours),
                self.seconds: (60, self.minutes),
            }[unit]
            roll_from, roll_to = rollover - 1, 0
            if d == -1:
                roll_from, roll_to = roll_to, roll_from
            if carry is not None:
                carry = delta(carry, d)
            return If(unit == roll_from, *(
                       [unit.eq(roll_to)] + (
                           [carry] if carry else []
                   ))).Else(unit.eq(unit + d))

        self.sync += [
            If(~self.tick,
                If(self.inc_hours, delta(self.hours, 1)),
                If(self.dec_hours, delta(self.hours, -1)),
                If(self.inc_minutes, delta(self.minutes, 1)),
                If(self.dec_minutes, delta(self.minutes, -1)),
            ),
            If(self.tick, delta(self.seconds, 1)),
        ]

# CoreFSM ------------------------------------------------------------------------------------------

class CoreFSM(Module):
    def __init__(self):
        # Module's interface
        self.tick    = Signal()  # input
        self.seconds = Signal(6) # output
        self.minutes = Signal(6) # output
        self.hours   = Signal(5) # output

        # Set interface
        self.inc_minutes = Signal() # input
        self.inc_hours   = Signal() # output

        # # #

        self.submodules.fsm = fsm = FSM(reset_state="IDLE")

        fsm.act("IDLE",
            If(self.tick,
                NextState("INC_SECONDS")
            ),
        )

        fsm.act("INC_SECONDS",
            If(self.seconds == 59,
                NextValue(self.seconds, 0),
                NextState("INC_MINUTES"),
            ).Else(
                NextValue(self.seconds, self.seconds + 1),
                NextState("IDLE"),
            ),
        )

        fsm.act("INC_MINUTES",
            If(self.minutes == 59,
                NextValue(self.minutes, 0),
                NextState("INC_HOURS"),
            ).Else(
                NextValue(self.minutes, self.minutes + 1),
                NextState("IDLE"),
            ),
        )

        fsm.act("INC_HOURS",
            If(self.hours == 23,
                NextValue(self.hours, 0),
            ).Else(
                NextValue(self.hours, self.hours + 1),
            ),
            NextState("IDLE")
        )

# Main ---------------------------------------------------------------------------------------------

if __name__ == '__main__':
    # Seven segment simulation
    print("Core simulation")
    # Uncomment the one you want to simulate
    # dut = Core()
    dut = CoreFSM()

    def show_time(cycle, hours, minutes, seconds):
        print("cycle %d: hh:%02d, mm:%02d, ss:%02d" %(cycle, hours, minutes, seconds))

    def dut_tb(dut):
        yield dut.tick.eq(1) # Tick active on each cycle
        for i in range(3600*48):
            yield
            show_time(i,
                (yield dut.hours),
                (yield dut.minutes),
                (yield dut.seconds))

    run_simulation(dut, dut_tb(dut), vcd_name="core.vcd")
