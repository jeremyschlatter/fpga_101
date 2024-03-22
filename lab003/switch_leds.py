import client

wb = client.connect()

while True:
    wb.regs.leds_out.write(wb.regs.switches_in.read())
