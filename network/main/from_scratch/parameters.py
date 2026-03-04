import numpy as np


learning_rate = 0.01
num_epochs = 10
batch_size = 32

layers = [32*32, 128, 64, 5] # Input layer (flattened image), hidden layers, output layer (5 classes)

#attribuer des poids aléatoires pour chaque couche
weights = []
for i in range(len(layers) - 1):
    weight_matrix = np.random.randn(layers[i], layers[i+1]) * np.sqrt(2 / layers[i]) # He initialization
    weights.append(weight_matrix)

#attribuer des biais aléatoires pour chaque couche
biais = []
for i in range(1, len(layers)):
    biais_vector = np.zeros(layers[i]) # On initialise les biais à zéro
    biais.append(biais_vector)
