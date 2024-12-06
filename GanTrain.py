import torch
import torch.nn as nn
import torch.optim as optim
import torch.utils.data as data
import json
import numpy as np


# Dataset class to load and preprocess game data
class MovesDataset(data.Dataset):
    def __init__(self, json_file, max_len=None):
        with open(json_file, 'r') as f:
            self.data = json.load(f)

        # Calculate max_len if not provided
        if max_len is None:
            self.max_len = max(len(game['moves']) for game in self.data)
        else:
            self.max_len = max_len

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        moves = np.array(self.data[idx]['moves'], dtype=np.int64)
        start_pos = self.data[idx]['start_pos']
        end_pos = self.data[idx]['end_pos']
        score = self.data[idx]['score']

        # Pad moves to max_len
        padding = self.max_len - len(moves)
        if padding > 0:
            moves = np.pad(moves, ((0, padding), (0, 0)), mode='constant', constant_values=0)

        moves_tensor = torch.tensor(moves, dtype=torch.float)
        start_end_tensor = torch.tensor(start_pos + end_pos, dtype=torch.float)  # Combine start and end
        score_tensor = torch.tensor(score, dtype=torch.float)

        return {'moves': moves_tensor, 'start_end': start_end_tensor, 'score': score_tensor}


# Function to load data
def load_data(json_file):
    dataset = MovesDataset(json_file)
    return torch.utils.data.DataLoader(dataset, batch_size=32, shuffle=True)


# Define the Generator class
class Generator(nn.Module):
    def __init__(self, path_length):
        super(Generator, self).__init__()
        self.path_length = path_length
        self.fc1 = nn.Linear(4 + 16, 128)  # 4 for start/end, 16 for noise
        self.fc2 = nn.Linear(128, 256)
        self.fc3 = nn.Linear(256, path_length * 2)  # Output (x, y) pairs for path_length moves

    def forward(self, start_end, noise):
        x = torch.cat([start_end, noise], dim=1)  # Combine start_end and noise
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = torch.tanh(self.fc3(x))  # Normalize output
        return x.view(-1, self.path_length, 2)


# Define the Discriminator class
class Discriminator(nn.Module):
    def __init__(self, path_length):
        super(Discriminator, self).__init__()
        self.fc1 = nn.Linear(path_length * 2 + 4, 256)
        self.fc2 = nn.Linear(256, 128)
        self.fc3 = nn.Linear(128, 1)

    def forward(self, paths, start_end):
        x = torch.cat([paths.view(paths.size(0), -1), start_end], dim=1)
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = torch.sigmoid(self.fc3(x))
        return x


# Training loop for the GAN
def train_gan(generator, discriminator, d_optimizer, g_optimizer, data_loader, path_length, epochs=100):
    criterion = nn.BCELoss()

    for epoch in range(epochs):
        for batch in data_loader:
            real_moves = batch['moves']
            start_end = batch['start_end']
            real_labels = torch.ones(real_moves.size(0), 1)
            fake_labels = torch.zeros(real_moves.size(0), 1)

            # Train Discriminator
            d_optimizer.zero_grad()

            # Real paths
            real_output = discriminator(real_moves, start_end)
            real_loss = criterion(real_output, real_labels)

            # Fake paths
            noise = torch.randn(real_moves.size(0), 16)  # Noise vector
            fake_moves = generator(start_end, noise)
            fake_output = discriminator(fake_moves, start_end)
            fake_loss = criterion(fake_output, fake_labels)

            # Total discriminator loss
            d_loss = real_loss + fake_loss
            d_loss.backward()
            d_optimizer.step()

            # Train Generator
            g_optimizer.zero_grad()

            # Fool discriminator
            fake_moves = generator(start_end, noise)
            fake_output = discriminator(fake_moves, start_end)
            g_loss = criterion(fake_output, real_labels)  # Generator tries to make fake look real

            g_loss.backward()
            g_optimizer.step()

        print(f"Epoch [{epoch + 1}/{epochs}], d_loss: {d_loss.item():.4f}, g_loss: {g_loss.item():.4f}")


# Save the trained model
def save_model(generator):
    torch.save(generator.state_dict(), 'botModel.pth')
    print("Model saved as botModel.pth")


# Main execution
if __name__ == "__main__":
    # Load data
    json_file = 'game_data.json'  # Ensure this file is uploaded to Colab
    data_loader = load_data(json_file)

    # Hyperparameters
    path_length = 42  # Max length of paths
    epochs = 100
    learning_rate = 0.0002

    # Initialize models
    generator = Generator(path_length)
    discriminator = Discriminator(path_length)

    # Optimizers
    d_optimizer = optim.Adam(discriminator.parameters(), lr=learning_rate, betas=(0.5, 0.999))
    g_optimizer = optim.Adam(generator.parameters(), lr=learning_rate, betas=(0.5, 0.999))

    # Train the GAN
    train_gan(generator, discriminator, d_optimizer, g_optimizer, data_loader, path_length, epochs)

    # Save the generator model
    save_model(generator)
