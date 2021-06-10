import torch
import torchvision


class BatchUnflatten(torch.nn.Module):
    def __init__(self, input_size, embeddings_size):
        super(BatchUnflatten, self).__init__()
        self.input_size = input_size
        self.embeddings_size = embeddings_size

    def forward(self, x):
        return torch.reshape(x, [-1, self.input_size, self.embeddings_size])


class CTNet(torch.nn.Module):
    def __init__(self, input_size, hidden_size=128, n_classes=2):
        super(CTNet, self).__init__()
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.n_classes = n_classes

        self.embeddings_size = 2048
        self.embeddings = torchvision.models.resnet50(pretrained=False)
        self.embeddings.fc = BatchUnflatten(self.input_size, self.embeddings_size)

        self.lstm = torch.nn.LSTM(self.embeddings_size, self.hidden_size, batch_first=True)
        self.fc = torch.nn.Linear(self.input_size * self.hidden_size, self.n_classes)

    def forward(self, x):
        # [B, L, 224, 224] -> [B * L, 224, 224]
        x = x.reshape([-1, 224, 224])

        # [B * L, 224, 224] -> [B * L, 3, 224, 224]
        x = torch.stack([x, x, x], dim=1)

        # [B * L, 3, 224, 224] -> [B, L, S]
        x = self.embeddings(x)

        # [B, L, S] -> [B, L, H]
        x, _ = self.lstm(x)

        # [B, L, H] -> [B, L * H]
        x = x.reshape([-1, self.input_size * self.hidden_size])

        # [B, L * H] -> [B, C]
        x = self.fc(x)
        return x
