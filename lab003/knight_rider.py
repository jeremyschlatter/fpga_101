import time

import client

wb = client.connect()

i = 0
delta = 1
while True:
    wb.regs.leds_out.write(1 << i)
    i += delta
    if i == 15 or i == 0:
        delta = -delta
    time.sleep(0.02)
