from torch import nn
import torch


class Network(nn.Module):
    def __init__(self, device: str, hidden_size: int = 512, num_conv_layers: int = 1, num_dense_layers: int = 2, activation: str = 'relu'):
        super().__init__()
        self.device = device

        if num_conv_layers < 1 or num_conv_layers > 3:
            raise ValueError(f"num_conv_layers must be between 1 and 3, got {num_conv_layers}")
        if activation not in ('relu', 'sigmoid'):
            raise ValueError(f"activation must be 'relu' or 'sigmoid', got {activation}")

        # Build conv stack
        conv_channels = [1, 32, 64, 128]
        conv_layers = []
        for i in range(num_conv_layers):
            conv_layers += [
                nn.Conv2d(conv_channels[i], conv_channels[i + 1], kernel_size=3, stride=1, padding=1),
                nn.ReLU() if activation == 'relu' else nn.Sigmoid(),
                nn.MaxPool2d(kernel_size=2, stride=2),
            ]
        self.convolutional_layer = nn.Sequential(*conv_layers)

        self.flatten = nn.Flatten()

        # Compute flatten size with dummy tensor
        with torch.no_grad():
            dummy = torch.zeros(1, 1, 28, 28)
            flatten_size = self.flatten(self.convolutional_layer(dummy)).shape[1]

        # Build dense stack
        dense_layers = []
        in_features = flatten_size
        for _ in range(num_dense_layers):
            dense_layers += [
                nn.Linear(in_features, hidden_size),
                nn.ReLU() if activation == 'relu' else nn.Sigmoid(),
            ]
            in_features = hidden_size
        dense_layers.append(nn.Linear(in_features, 5))
        self.linear_layer = nn.Sequential(*dense_layers)

        self.to(device)

    def forward(self, x):
        x = self.convolutional_layer(x)
        x = self.flatten(x)
        x = self.linear_layer(x)
        return x

    def train_model(self, dataloader, loss_fn, optimizer):
        self.train()
        for batch, (X, y) in enumerate(dataloader):
            X, y = X.to(self.device), y.to(self.device)

            pred = self(X)
            loss = loss_fn(pred, y)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

    @torch.no_grad()
    def test_model(self, dataloader, loss_fn):
        size = len(dataloader.dataset)
        num_batches = len(dataloader)
        self.eval()
        test_loss, correct = 0, 0

        for X, y in dataloader:
            X, y = X.to(self.device), y.to(self.device)
            pred = self(X)
            test_loss += loss_fn(pred, y).item()
            correct += (pred.argmax(1) == y).type(torch.float).sum().item()

        avg_loss = test_loss / num_batches
        accuracy = 100 * (correct / size)

        print(f"Test Error: \n Accuracy: {accuracy:>0.1f}%, Avg loss: {avg_loss:>8f}")

        return avg_loss, accuracy
