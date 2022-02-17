import socket
import selectors

sel = selectors.DefaultSelector()

def server_loop():
    while True:
        events = sel.select(timeout=None)
        for key, mask in events:
            print("key.data: %s\n" % key.data)

