import tonic
import tonic.transforms as transforms
from torch.utils.data import DataLoader
import torch
import numpy as np
import h5py

DATADIR = "./data"
batch_size=16
sensor_size = (32, 32, 2)
frame_transform_test = transforms.Compose([transforms.Denoise(filter_time=10000),
                                      transforms.Downsample(spatial_factor=0.25),
                                      transforms.ToFrame(sensor_size=sensor_size,
                                                         n_time_bins=150)
                                    ])

test_ds = tonic.datasets.DVSGesture(save_to=DATADIR, transform=frame_transform_test, train=False)
test_dl = DataLoader(test_ds, batch_size=batch_size,
                         collate_fn=tonic.collation.PadTensors(batch_first=False))

nsamples = len(test_ds)
arr = np.empty((nsamples, 150, 2, 32, 32), dtype='<i2')
labels =np.empty((nsamples, 1), dtype='<i1')
for i, (val, l) in enumerate(test_ds):
    arr[i] = val
    labels[i] = l

print("DONE.")

arr = np.reshape(arr, (nsamples, 150, 32, 32, 2))

hf = h5py.File("test_set.hdf5", "w")
a = hf.create_dataset("data", (arr.shape), dtype='i2')
b = hf.create_dataset("labels", (labels.shape), dtype='i1')
a[:] = arr
b[:] = labels
hf.close()

print("DONE.")

with open("test_data.npy", "wb") as fp:
    np.save(fp, arr)
with open("test_labels.npy", "wb") as fp:
    np.save(fp, labels)

print("DONE.")
