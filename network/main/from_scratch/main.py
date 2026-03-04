import numpy as np
from network.main.from_scratch.image_processing import get_network_data

################## DATA ##################
base_path = "dataset/dataset-data/training-data/"
train_data, test_data, train_labels, test_labels = get_network_data(base_path, 0.8)

################## PARAMETERS ##################
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

################## NETWORK ##################
def relu(x):
    return np.maximum(0, x)

def softmax(val_final_layer):
    exp_logits = np.exp(val_final_layer - np.max(val_final_layer)) # Numerical stability
    return exp_logits / np.sum(exp_logits)

# ce code fonctionne pour les NN traditionnels, semblable au dense layer
val_input = train_data[0].flatten() # logiquement on devrait avoir des differentes dimensions si on faisait un CNN du au max pooling.
val_couche1 = relu(val_input@weights[0] + biais[0]) 
val_couche2 = relu(val_couche1@weights[1] + biais[1])
val_final_layer = val_couche2@weights[2] + biais[2]
predictions = softmax(val_final_layer)
print("Predicted probabilities:", predictions)