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
