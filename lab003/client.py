from contextlib import chdir, contextmanager

from litex import RemoteClient

@contextmanager
def connect():
    with chdir('test'):
        wb = RemoteClient()
        wb.open()
    try:
        yield wb
    finally:
        wb.regs.leds_out.write(0)
