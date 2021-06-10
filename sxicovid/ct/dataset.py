import os
import torch
import torchvision
import pandas as pd

from PIL import Image as pil
from PIL import ImageOps as pilops

ROOT_DATAPATH = 'datasets/covidx-ct'


class CXR2Dataset(torch.utils.data.Dataset):
    def __init__(self, path, dataframe, equalize=False, augment=False):
        self.path = path
        self.equalize = equalize

        # Extract the filenames and classes from the dataframe
        self.filenames = dataframe['filename'].to_numpy()
        self.targets = dataframe['class'].to_numpy()

        # Initialize data transforms
        transforms = []
        if augment:
            transforms.extend([
                torchvision.transforms.RandomHorizontalFlip(),
                torchvision.transforms.RandomVerticalFlip(),
                torchvision.transforms.RandomAffine(
                    degrees=20.0,
                    translate=(0.1, 0.1),
                    scale=(0.9, 1.1),
                    interpolation=torchvision.transforms.InterpolationMode.BILINEAR  # use bilinear interpolation
                )
            ])
        transforms.append(torchvision.transforms.Normalize((0.5,), (0.5,)))  # normalize to (-1, 1)
        self.transform = torchvision.transforms.Compose(transforms)
        self.to_tensor = torchvision.transforms.ToTensor()

    def __len__(self):
        return len(self.filenames)

    def __getitem__(self, i):
        # Obtain the filename and target
        filename = self.filenames[i]
        target = self.targets[i]

        # Load and transform the image
        slices = []
        with pil.open(os.path.join(self.path, filename)) as img:
            for i in range(img.n_frames):
                if self.equalize:
                    data = self.to_tensor(pilops.equalize(img))
                else:
                    data = self.to_tensor(img)
                slices.append(data)
                if i != img.n_frames - 1:
                    img.seek(img.tell() + 1)
        data = self.transform(torch.cat(slices))
        return data, target

    def get_targets(self):
        return self.targets


def load_datasets(n_classes=2, equalize=False, augment=True):
    assert n_classes == 2 or n_classes == 3, 'Whether to use the 3 classes version or not'

    # Set the class converter if n_classes == 2
    if n_classes == 2:
        converters = {'class': lambda c: 0 if c == '1' else 1 if c == '2' else 0}
    else:
        converters = {'class': lambda c: int(c)}

    # Load the train, validation and test dataframes
    train_filepath = os.path.join(ROOT_DATAPATH, 'train.csv')
    valid_filepath = os.path.join(ROOT_DATAPATH, 'valid.csv')
    test_filepath = os.path.join(ROOT_DATAPATH, 'test.csv')
    train_df = pd.read_csv(train_filepath, usecols=['filename', 'class'], converters=converters)
    valid_df = pd.read_csv(valid_filepath, usecols=['filename', 'class'], converters=converters)
    test_df = pd.read_csv(test_filepath, usecols=['filename', 'class'], converters=converters)

    # Instantiate the datasets (notice data augmentation on train data)
    train_images_path = os.path.join(ROOT_DATAPATH, 'train')
    valid_images_path = os.path.join(ROOT_DATAPATH, 'valid')
    test_images_path = os.path.join(ROOT_DATAPATH, 'test')
    train_data = CXR2Dataset(train_images_path, train_df, equalize=equalize, augment=augment)
    valid_data = CXR2Dataset(valid_images_path, valid_df, equalize=equalize, augment=False)
    test_data = CXR2Dataset(test_images_path, test_df, equalize=equalize, augment=False)
    return train_data, valid_data, test_data