""" Save machine learning data sets to a common location, and load them without
    having to specify a path.
"""

from os import path
from pathlib import Path
import numpy as np

from .download_utils import download


_path = Path(path.dirname(path.abspath(__file__)))


__all__ = ["load", "download", "get_path"]


def _get_dataset_path(dataset_name):
    return _path / dataset_name

def get_path(): return _get_dataset_path("cifar-10-python.npz")


def load(fname='cifar-10-python.npz'):
    """ The CIFAR-10 dataset consists of 60000x3x32x32 color images in 10 
        classes, with 6000 images per class. There are 50000 training images 
        and 10000 test images.

        The labels are formatted using one-hot encoding.

        https://www.cs.toronto.edu/~kriz/cifar.html

        Returns
        -------
        Tuple[numpy.ndarray, numpy.ndarray, numpy.ndarray, numpy.ndarray]
            training-data, training-labels, test-data, test-labels

        Notes
        -----
        A tuple of the categories corresponding to the data's integer labels are bound as an
        attribute of this function:

            `cifar10.load.labels`
        """
    

    if not (_path / fname).exists():
        msg = """ Data not found! Please download the data (cifar-10-python.npz) using 
                 `cifar10.download()`"""
        raise FileNotFoundError(msg)

    with np.load(str(_path / fname)) as data:
        xtr, ytr, xte, yte = tuple(data[key] for key in ['x_train', 'y_train', 'x_test', 'y_test'])
    print("cifar-10 loaded")
    return xtr, ytr, xte, yte

load.labels = ("airplane",
                       "automobile",
                       "bird",
                       "cat",
                       "deer",
                       "dog",
                       "frog",
                       "horse",
                       "ship",
                       "truck")
