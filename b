import numpy as np

import ss

# print(np.random.lognormal(np.log(10710), np.log(25032), 10))

s = ss.init_conn()
s.sendall('hello')
