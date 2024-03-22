import client

with client.connect() as wb:
    while True:
        wb.regs.leds_out.write(wb.regs.switches_in.read())
