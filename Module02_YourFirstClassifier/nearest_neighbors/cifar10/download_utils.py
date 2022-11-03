from pathlib import Path
from os import path
import numpy as np 

__all__ = ["download"]

_path = Path(path.dirname(path.abspath(__file__)))


def _md5_check(fname):
    """ Reads in data from disk and returns md5 hash"""
    import hashlib
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def download(path=None):
    """ Download the cifar-10 dataset and save it as a .npz archive.
        md5 check-sum verficiation is performed.

        Parameters
        ----------
        path : Optional[str, pathlib.Path]
            path to .npz file to be saved (including the filename itself)
            
            if `None`, path = path/to/DataSets/datasets/cifar-10-python.npz"""

    def _download_cifar10(path=None, tmp_dir=None):
        server_url = "https://www.cs.toronto.edu/~kriz/cifar-10-python.tar.gz"
        md5_checksum = "c58f30108f718f92721af3b95e74349a"
        if tmp_dir is None:
            tmp_dir = Path(".") / "_tmp_dir"
        tmp_file = tmp_dir / "__tmp_cifar10.bin" 
        
        import tarfile
        import urllib.request
        import os

        def unpickle(file):
            import pickle
            with open(file, 'rb') as fo:
                return pickle.load(fo, encoding='bytes')
                
        path = Path(path) if path is not None else _path / 'cifar-10-python.npz'
            
        if path.is_file():
            print("File already exists:\n\t{}".format(path))
            return None
        
        train = np.empty((50000, 3072), dtype=np.uint8)
        test = np.empty((10000, 3072), dtype=np.uint8)

        print("Downloading from: {}".format(server_url))
        
        try:
            with urllib.request.urlopen(server_url) as response:
                with open(tmp_file, 'wb') as handle:
                    handle.write(response.read())

                assert _md5_check(tmp_file) ==  md5_checksum, "md5 checksum did not match!.. deleting file"
                
                with tarfile.open(tmp_file, 'r:gz') as f:
                    def is_within_directory(directory, target):
                        
                        abs_directory = os.path.abspath(directory)
                        abs_target = os.path.abspath(target)
                    
                        prefix = os.path.commonprefix([abs_directory, abs_target])
                        
                        return prefix == abs_directory
                    
                    def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
                    
                        for member in tar.getmembers():
                            member_path = os.path.join(path, member.name)
                            if not is_within_directory(path, member_path):
                                raise Exception("Attempted Path Traversal in Tar File")
                    
                        tar.extractall(path, members, numeric_owner=numeric_owner) 
                        
                    
                    safe_extract(f, tmp_dir)
        finally:
            if os.path.isfile(tmp_file):
                os.remove(tmp_file)
            
        train_labels = []
        for i in range(1, 6):
            d = unpickle(tmp_dir / "cifar-10-batches-py/data_batch_{}".format(i))
            train[(i - 1)*10000:i*10000] = np.asarray(d[b'data'])
            train_labels += d[b'labels']

        train = train.reshape(-1, 3, 32, 32)
        train_labels = np.asarray(train_labels)

        print("Writing train data:")
        print("Images: ", train.shape, train.dtype)
        print("Labels: ", train_labels.shape, train_labels.dtype)

        d = unpickle(tmp_dir / "cifar-10-batches-py/test_batch")
        test = np.asarray(d[b'data']).reshape(-1, 3, 32, 32)
        test_labels = np.array(d[b'labels'])

        print("Writing test data:")
        print("Images: ", test.shape, test.dtype)
        print("Labels: ", test_labels.shape, test_labels.dtype)
        
        print("Saving to: {}".format(path))
        with path.open(mode="wb") as f:
            np.savez_compressed(f, x_train=train, y_train=train_labels, 
                                x_test=test, y_test=test_labels)
        return

    import os
    import shutil
    tmp_dir = Path(".") / "_tmp_dir_"
    if tmp_dir.exists():
        print("Directory: {} already exists - an intermediate directory needs to be constructed here".format(tmp_dir))
        print("move/delete that directory and try again.")
        return None
    else:
        tmp_dir.mkdir()

    try:
        _download_cifar10(path, tmp_dir)
    finally:
        if tmp_dir.exists():
            shutil.rmtree(tmp_dir)
