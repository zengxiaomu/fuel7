import sys
import socket
import selectors
import time
import numpy as np

#
# global random sequence variables
#

seq = (0)
seq_index = 1

#
# generate random sequnce based on probability density function 
#

def gen_random_seq(c=10):
    #
    # easy peasy
    #
    seq = np.random.exponential(1.25, 10)
    print(seq)

#
# save random sequence to file
#

def save_seq(fn='seq.txt'):
    print(seq)
    # 
    # save to file for re-use 
    # This could be useful if generating
    # random exponential sequence in C code
    # is too hard...just read it from a file!
    #

#
# read random sequence from file
#

def read_seq(fn='seq.txt'):
    print(seq)
    #
    # in case numpy is not available..read it from a file
    #
    
#
# VoIP 
#

def send_active_packet(size=122):
    print(f"send active packet size {size}")
    #
    # How to actually send VoIP packets in python? Maybe ask Tomas?
    #

def send_silent_packet(size=0):
    print(f"send silent packet size {size}")
    #
    # How to actually send VoIP packets in python? 
    #

def talking_state():
    duration = seq[seq_index]
    seq_index += 1
    #
    # during the duration, generate 12.2K data per seconds
    #
    block = int(duration*100)
    #
    # One block is 10 ms, we shall send 122 bytes per block
    #
    for i in range(0, block, 1):
        send_active_packet(122)
        
def silent_state():
    duration = seq[seq_index]
    seq_index += 1
    #
    # during the duration, generate ??? data per seconds
    # we need to send "silent packet" but what does that
    # actually mean? 
    #
    block = int(duration*100)
    #
    # One block is 10 ms, we shall send 0? bytes per block
    #
    for i in range(0, block, 1):
        send_silent_packet(0)
        

#
# VoIP Call manager
#

def call_manager(total=10, duration=10):
    print(f"total calls: {total} total time: {duration}")
    #
    # Simulate total=10 number of calls
    #
    # SO, should I use threads with 1 thread per call? 
    #
    # No. Only use threads as last resort. 
    #
    # If efficency is a concern, we can implement threads in C code later
    #
    block = int(duration*100)
    #
    # init call state
    for i in range(0, total-1, 1):
        call_state[i] = int(np.random(1)) # 0 or 1
        timer[i] = seq[seq_index]
        seq_index += 1
    #
    # Now start call processes
    #
    for b in range(0, block, 1):
        for i in range(0, total-1, 1):
            if call_state[i] == 0:
                send_silent_packet(0)
            elif call_state[i] == 1:
                send_active_packet(122)
            if b == timer[i]:
                #
                # transition between talk state and silent state
                #
                if call_state[i] == 0:
                    call_state[i] = 1
                    timer[i] += seq[seq_index]
                    seq_index+= 1
                elif call_state[i] == 1:
                    call_state[i] = 0
                    timer[i] += seq[seq_index]
                    seq_index += 1
        time.sleep(0.01)  # sleep for 10 ms


#
# Networking default values
#

default_host='127.0.0.1'
default_port=1729

#
# global variables sel
#

sel = selectors.DefaultSelector()

#
# accept client connection
#

def accept_conn(key, mask):
    s = key.fileobj
    s.setblocking(True)
    conn, addr = s.accept()
    s.setblocking(False)
    print(f"Accepted connection from {addr}")
    conn.setblocking(False)
    sel.register(conn, selectors.EVENT_READ, data=service_conn)

#
# start socket server
#

def init_server(host=default_host, port=default_port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind((host, port))
        s.listen()
    except OSError as msg:
        print(msg)
        return 0
    print(f"listening on {(host, port)}")
    s.setblocking(False)
    sel.register(s, selectors.EVENT_READ, data=accept_conn)
    return s

#
# global variables ss
#

ss = init_server()

#
# start socket client
#

def init_conn(host=default_host, port=default_port):
    print(f"Starting connection to {(host, port)}")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    err = s.connect_ex((host, port))
    if err != 0:
        print(f"Connection failed: {err}")
        return err
    else:
        s.setblocking(False)
        # sel.register(s, selectors.EVENT_READ, read)
        return s

#
# receive client message
#

def service_conn(key, mask):
    s = key.fileobj
    peer = s.getpeername()
    if mask & selectors.EVENT_READ:
        print(f"receive data from {peer}")
        recv_data = s.recv(1024)
        if recv_data:
            print(f"data received {recv_data}")
        else:
            print(f"Closing connection to {peer}")
            sel.unregister(s)
            s.close()
    if mask & selectors.EVENT_WRITE:
        print(f"write data to {peer}")

#
# main loop for handling socket events
#

def server_loop():
    try:
        while True:
            events = sel.select(timeout=0)
            for key, mask in events:
                callback = key.data
                callback(key, mask)
    except KeyboardInterrupt:
        print("keyboard interrupt, exiting")
    finally:
        sel.close()

