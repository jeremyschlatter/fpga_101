from contextlib import chdir

from litex import RemoteClient

def connect():
    with chdir('test'):
        wb = RemoteClient()
        wb.open()
    return wb
