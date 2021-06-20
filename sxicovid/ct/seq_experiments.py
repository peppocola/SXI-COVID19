from sxicovid.ct.models import CTSeqNet
from sxicovid.ct.dataset import load_sequence_datasets
from sxicovid.utils.train import train_classifier


if __name__ == '__main__':
    # Load the datasets
    train_data, valid_data, test_data = load_sequence_datasets()

    # Instantiate the model
    model = CTSeqNet(input_size=16, num_classes=3, load_embeddings=True)
    print(model)

    # Train the classifier
    train_classifier(
        model, train_data, valid_data, chkpt_path='ct-checkpoints/ct-resnet50-lstm-att2.pt',
        lr=1e-4, optimizer='adam', batch_size=8, epochs=25, patience=5, weight_decay=5e-3,
        n_workers=2
    )
