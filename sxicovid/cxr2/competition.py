import os
import torch

from tqdm import tqdm
from PIL import Image as pil

from sxicovid.cxr2.metrics import load_model
from sxicovid.cxr2.dataset import load_competition_dataset
from sxicovid.cxr2.preprocessing import image_preprocess


COMPETITION_IMAGES_PATH = '/hdd/Datasets/covidx-cxr2/competition_test'
PREPROC_COMPETITION_IMAGES_PATH = 'datasets/covidx-cxr2/competition/images'


def preprocess_competition_images():
    for idx in tqdm(range(1, 401)):
        filename = '{}.png'.format(idx)
        filepath = os.path.join(COMPETITION_IMAGES_PATH, filename)
        preproc_filepath = os.path.join(PREPROC_COMPETITION_IMAGES_PATH, filename)
        with pil.open(filepath) as img:
            preproc_img = image_preprocess(img, greyscale=True, crop=True, size=(224, 224), remove_top=True)
            preproc_img.save(preproc_filepath)


if __name__ == '__main__':
    # Load the model
    equalize = True
    model = load_model('ResNet50', equalize=equalize)

    # Load the dataset
    dataset = load_competition_dataset(equalize=equalize)

    # Get the device to use
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print('Test using device: ' + str(device))

    # Move the model to device
    model.to(device)

    # Make sure the model is set to evaluation mode
    model.eval()

    # Setup the data loader
    data_loader = torch.utils.data.DataLoader(dataset, batch_size=4, shuffle=False, num_workers=4)

    # Make the predictions
    y_pred = []
    with torch.no_grad():
        for inputs in data_loader:
            inputs = inputs.to(device)
            outputs = torch.log_softmax(model(inputs), dim=1)
            predictions = torch.argmax(outputs, dim=1)
            y_pred.extend(predictions.cpu().tolist())
    print(y_pred)

    with open('submission.txt', 'w') as f:
        for pred in y_pred:
            f.write(str(pred) + '\n')
