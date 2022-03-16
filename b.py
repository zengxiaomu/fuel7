import numpy as np
import time
import ss

# print(np.random.lognormal(np.log(10710), np.log(25032), 10))

# ss.config.read('ss.ini')

# for k in ss.config.sections():
    # print("[%s]" % k)
    # for key in ss.config[k]:
        # print("%s = %s " % (key, ss.config[k][key]))

ss.gen_random_seq()
ss.init_voip()
ss.save_seq()
ss.get_dl_jitter()

while True:
    delta = ss.voip_get_delta()
    time.sleep(2)

exit(0)

s = ss.init_conn()
s2 = ss.init_conn()
s3 = ss.init_conn()
s4 = ss.init_conn()
s5 = ss.init_conn()
while True:
    try:
        s.send('hello'.encode())
        s2.send('hello 2'.encode())
        s3.send('hello 3'.encode())
        s4.send('hello 4'.encode())
        s5.send('hello 5'.encode())
    except OSError as err:
        print(err)
    time.sleep(2)
    print("looping..")
