from datetime import datetime, timedelta
import time

import client

with client.connect_ctx() as wb:

    def display_write(sel, value):
        client.display_write(wb, sel, value)

    def display_time(hour, minute, second):
        display_write(0, second%10)
        display_write(1, (second//10)%10)
        display_write(2, minute%10)
        display_write(3, (minute//10)%10)
        display_write(4, hour%10)
        display_write(5, (hour//10)%10)

    center = 0
    down = 1
    left = 2
    right = 3
    up = 4

    was_pressed = [False] * 5
    all_released = False

    hms = (0, 0, 0)
    delta = timedelta()
    while True:
        t = datetime.now() + delta
        if (n := (t.hour, t.minute, t.second)) != hms:
            hms = n
            display_time(*hms)

        buttons = wb.regs.buttons_in.read()
        if buttons == 0 and all_released:
            continue
        pressed = [((1 << i) & buttons) > 0 for i in range(5)]
        released = [was_pressed[i] and not pressed[i] for i in range(5)]
        was_pressed = pressed
        all_released = not any(pressed)

        if released[up]:
            delta += timedelta(hours=1)
        if released[down]:
            delta += timedelta(hours=-1)
        if released[right]:
            delta += timedelta(minutes=1)
        if released[left]:
            delta += timedelta(minutes=-1)
        if released[center]:
            delta = timedelta()
