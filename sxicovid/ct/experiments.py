import os

from sxicovid.ct.models import CTNet
from sxicovid.ct.dataset import load_datasets
from sxicovid.utils.train import train_classifier
from sxicovid.utils.evaluate import test_classifier

EXPERIMENTS_PATH = 'ct-experiments'


if __name__ == '__main__':
    if not os.path.isdir(EXPERIMENTS_PATH):
        os.mkdir(EXPERIMENTS_PATH)

    # Load the datasets
    train_data, valid_data, test_data = load_datasets()

    # Instantiate the model
    model = CTNet(base='resnet50')
    print(model)

    batch_size = 32

    train_classifier(
        model, train_data, valid_data,
        lr=1e-3, optimizer='adam', batch_size=batch_size, epochs=100, patience=5, n_workers=2
    )

    report, _ = test_classifier(
        model, test_data, batch_size=batch_size, n_workers=2
    )

    print(report)
