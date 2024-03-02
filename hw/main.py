import pynq
from pynq import Overlay
from pynq import allocate
import numpy as np
import sys
np.set_printoptions(threshold=sys.maxsize)

overlay = Overlay("/home/ubuntu/isfpga-fabrizio/design_1_wrapper.bit")


# Input samples.
# data = np.array((SAMPLES, TIMESTEPS*HI*WI*CI), dtype='<i1')

data = np.load(open("test_data.npy", "rb"))
labels = np.load(open("test_labels.npy", "rb"))

SAMPLES, TIMESTEPS, HI, WI, CI = data.shape

results = np.array((SAMPLES,))

# Allocating data structures to communicate with the IP.
din = allocate(shape=(TIMESTEPS*HI*WI*CI,), dtype='<i2')
dout = allocate(shape=(TIMESTEPS*12,), dtype=bool)

# Configuring memory addresses for the IP.
overlay.wrapper_1.write(0x10, din.device_address)
overlay.wrapper_1.write(0x14, din.device_address >> 32)

overlay.wrapper_1.write(0x1c, dout.device_address)
overlay.wrapper_1.write(0x20, dout.device_address >> 32)

for sample in range(SAMPLES):
    # Writing the sample to the IP.
    din[:] = data[sample][:]
    din.sync_to_device()

    # Starting inference.
    overlay.wrapper_1.write(0x00, 1)

    # Waiting for execution to finish.
    while not overlay.wrapper_1.read(0x00) & 2:
        pass

    # Reading out data.
    dout.sync_from_device()
    tmp = np.zeros((11,))
    for t in range(TIMESTEPS):
        for i in range(11):
        tmp[i] += dout[t*TIMESTEPS + i]

    results[sample] = np.argmax(tmp)
