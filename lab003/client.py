from contextlib import chdir, contextmanager

from litex import RemoteClient

def connect():
    with chdir('test'):
        wb = RemoteClient()
        wb.open()
    return wb

@contextmanager
def connect_ctx():
    wb = connect()
    try:
        yield wb
    finally:
        wb.regs.leds_out.write(0)
        for i in range(6):
            display_write(wb, i, 0)
        wb.close()

def display_write(wb, sel, value):
    wb.regs.display_sel.write(sel)
    wb.regs.display_value.write(value)
    wb.regs.display_write.write(1)
