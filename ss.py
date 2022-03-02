import sys
import socket
import selectors
import time
import numpy as np
import configparser as cp

#
# global config hash variable
#

config = cp.ConfigParser()
read_config_hash_status = False
config_global = {}

#
# read config hash
#

def read_config_hash(fn='ss.ini'):
    global config_global
    config.read(fn)
    read_config_hash_status = True
    config_global = config['Global']

#
# global random sequence variables
#

seq = []
seq_index = 0
packet_seq = []  

#
# generate random sequnce based on probability density function 
#

def gen_random_seq(c=1000):
    global seq

    if read_config_hash_status == False:
        read_config_hash()
    c = int(config_global['MaxRandSeqCount'])
    m = int(config_global['DistMean'])  # Unit of DistMean is nanosecond

    #
    # easy peasy
    #
    
    seq = np.random.exponential(m, c)
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
# VoIP: get talking state packets per second
#

def get_talking_packet_rate():
   size = int(config_global['PktSizeTalking'])
   rate = int(config_global['SourceRate'])
   pkt_rate = int (rate / size)
   print("talking rate %s" % pkt_rate)
   return(pkt_rate)

#
# VoIP: get silent state packets per second
#

def get_silent_packet_rate():
   size = int(config_global['PktSizeSilent'])
   rate = int(config_global['SourceRateSilent'])
   pkt_rate = int (rate / size)
   print("silent rate %s" % pkt_rate)
   return(pkt_rate)

#
# generate packet sequence
#

def save_packet_seq():
    f = open('packets.txt', 'w')
    for (delta, size) in packet_seq:
        f.write("%s %s\n" % (delta, size))
    f.close()

def get_talking_packet_size():
    return(int(config_global['PktSizeTalking']))

def get_silent_packet_size():
    return(int(config_global['PktSizeSilent']))

def do_send_packet(rate):
    t = int(np.random.uniform(0, 1000))
    # print("do_send_packet: %s %s" % (t, rate))
    if t < rate:
        return True
    else:
        return False

def gen_packet_seq(c=100):
    global packet_seq
    pkt_rate_talking = get_talking_packet_rate()
    pkt_rate_silent = get_silent_packet_rate()
    pkt_size_talking = get_talking_packet_size()
    pkt_size_silent = get_silent_packet_size()
    delta = 0
    rate = pkt_rate_talking
    size = pkt_size_talking
    for i in range(0, c-1, 1):
        duration = int(seq[i])
        # print(size)
        for k in range(0, duration-1, 1):
            if do_send_packet(rate):
                packet_seq.append([delta*1000, size])
            delta += 1
        #
        # switch from/to talking/silent state
        #
        if (size == pkt_size_talking):
            size = pkt_size_silent
            rate = pkt_rate_silent
        else:
            size = pkt_size_talking
            rate = pkt_rate_talking

    # print(packet_seq)
    save_packet_seq()

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

