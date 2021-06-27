import torch


class LinearAttention1d(torch.nn.Module):
    """
    General linear attention with softmax normalization.
    """
    def __init__(self, in_features, out_features):
        super(LinearAttention1d, self).__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.gate = torch.nn.Linear(self.in_features, self.out_features, bias=False)

    def forward(self, x, g):
        g = g.unsqueeze(2)
        c = torch.bmm(self.gate(x), g)
        a = torch.softmax(c, dim=1)
        g = torch.sum(a * x, dim=1)
        return a.squeeze(2), g


class LinearAttention2d(torch.nn.Module):
    """
    Linear attention based on parametrized compatibility score function with softmax normalization.
    """
    def __init__(self, in_features, out_features):
        super(LinearAttention2d, self).__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.proj = None
        if self.in_features != self.out_features:
            self.proj = torch.nn.Conv2d(
                self.in_features, self.out_features,
                kernel_size=(1, 1), padding=(0, 0), bias=False
            )
        self.score = torch.nn.Conv2d(
            self.out_features, out_channels=1,
            kernel_size=(1, 1), padding=(0, 0), bias=False
        )

    def forward(self, x, g):
        b, _, h, w = x.size()
        if self.proj is not None:
            g = self.proj(g)
        c = self.score(x + g)
        a = torch.softmax(c.view(b, 1, -1), dim=2).view(b, 1, h, w)
        g = torch.mul(a.expand_as(x), x)
        g = g.view(b, self.out_features, -1).sum(dim=2)
        return a, g
