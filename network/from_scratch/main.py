# Pour exécuter le script, taper dans le terminal: py -m network.from_scratch.main

import numpy as np
from network.from_scratch.data_processing import get_emoji_data, load_mnist_data, get_shuffled_data
import math

################## DONNÉES ##################
# X, y = get_emoji_data("dataset/dataset-data/training-data/")
# X_train, X_test, y_train, y_test = get_shuffled_data(X, y, 5, 0.8)
X_train, X_test, y_train, y_test = load_mnist_data()

################## PARAMÈTRES ##################
dtype = np.float32
learning_rate = 0.01
num_epochs = 10
batch_size = 32

# Couche d'entrée (image aplatie), couches cachées, couche de sortie
# layers = [32*32, 128, 64, 5] # pour les emojis
layers = [28*28, 128, 64, 10] # pour mnist

# attribuer des poids aléatoires pour chaque couche
weights = [np.random.randn(layers[i+1], layers[i]).astype(dtype) * np.sqrt(2 / layers[i]) for i in range(len(layers)-1)] # He initialization
# PARLER DE HE INITIALIZATION SI ON L'UTILISE, SINON, JUSTE NP.RANDOM entre [-1, 1]
# attribuer des biais aléatoires pour chaque couche
bias = [np.zeros(l, dtype=dtype) for l in layers[1:]]

################## RÉSEAU ##################
def relu(Z):
    return np.maximum(0, Z)
def relu_prime(Z):
    return (Z > 0).astype(float) # quand x = 0, ça devrait être undefined, mais il faut faire un choix pratique
def softmax(z):
    exp_z = np.exp(z)
    return exp_z / (np.sum(exp_z))
def cost_prime(predictions, label):
    return predictions - label

def test():
    def forward(x):
        # Propagation avant
        sums = [np.zeros(l, dtype=dtype) for l in layers]
        activations = [np.zeros(l, dtype=dtype) for l in layers]
        activations[0] = x.flatten()

        for l in range(len(layers)-1):
            sums[l] = weights[l] @ activations[l] + bias[l]
            if l == len(layers) - 2:
                activations[l+1] = sums[l] # pas appliquer d'activation aux valeurs de la couche finale
            else:
                activations[l+1] = relu(sums[l])

        predictions = softmax(activations[-1])
        return predictions


    def is_prediction_good(output_layer, label):
        return label[np.argmax(output_layer)] == 1

    accuracy = 0
    for x, label in zip(X_test, y_test):
        prediction = forward(x)
        accuracy += 1 if is_prediction_good(prediction, label) else 0
    accuracy /= len(X_test)
    print(f"Model accuracy: {accuracy*100:.2f}%")


num_batch = math.ceil(len(X_train) / batch_size)

for epoch in range(num_epochs):

    # mélanger les données avant la création de nouveaux mini-lots
    perm = np.random.permutation(len(X_train))
    X_train = X_train[perm]
    y_train = y_train[perm]

    for batch in range(num_batch):
        start_index = batch*batch_size
        end_index = min((batch+1)*batch_size, len(X_train))
        real_batch_size = float(end_index - start_index)

        xs = X_train[start_index:end_index]
        labels = y_train[start_index:end_index]

        gradient_w = [np.zeros((layers[i+1], layers[i]), dtype=dtype) for i in range(len(layers)-1)]
        gradient_b = [np.zeros(l, dtype=dtype) for l in layers[1:]]

        for x, label in zip(xs, labels):
            # Propagation avant
            sums = [np.zeros(l, dtype=dtype) for l in layers]
            activations = [np.zeros(l, dtype=dtype) for l in layers]
            activations[0] = x.flatten()

            for l in range(len(layers)-1):
                sums[l] = weights[l] @ activations[l] + bias[l]
                if l == len(layers) - 2:
                    activations[l+1] = sums[l] # pas appliquer d'activation aux valeurs de la couche finale
                else:
                    activations[l+1] = relu(sums[l])

            predictions = softmax(activations[-1])

            # Propagation arrière
            error = cost_prime(predictions, label)
            for l in range(len(layers)-2, -1, -1):
                gradient_w[l] += error[:,None] @ activations[l][None,:]
                gradient_b[l] += error.copy()
                if l != 0:
                    error = (weights[l].T @ error) * relu_prime(sums[l-1])

        # Descente du gradient
        for i in range(len(layers)-1):
            weights[i] -= learning_rate * gradient_w[i] / real_batch_size
            bias[i] -= learning_rate * gradient_b[i] / real_batch_size
    print(f"---------- Epoch #{epoch+1} ----------")
    test()

# save model avec np.save