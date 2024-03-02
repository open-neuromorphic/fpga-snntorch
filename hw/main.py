import pynq
from pynq import Overlay
from pynq import allocate
import numpy as np
import sys
np.set_printoptions(threshold=sys.maxsize)

overlay = Overlay("/home/ubuntu/overlay0/design_1_wrapper.bit")

SAMPLES, TIMESTEPS, HI, WI, CI = 1, 25, 32, 32, 2

# Input samples.
data = np.array((SAMPLES, TIMESTEPS*HI*WI*CI), dtype='<i1')

# Allocating data structures to communicate with the IP.
din = allocate(shape=(TIMESTEPS*HI*WI*CI,), dtype='<i1')
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

    # Printing out  the data.
    print('\n' + '-'*80)
    print(dout)
    print('-'*80)

