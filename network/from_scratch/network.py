from turtle import width

import numpy as np
import math
from network.experimental.from_scratch_CNN.from_scratch import ConvLayer
from network.from_scratch.data_processing import load_mnist_data
from data_processing import get_emoji_data, get_shuffled_data

# Pour exécuter le script, taper dans le terminal: py -m network.from_scratch.network
#X, y = get_emoji_data("dataset/dataset-data/training-data/")
#input_train, input_test, label_train, label_test = get_shuffled_data(X, y, 5, 0.8)
input_train, input_test, label_train, label_test = load_mnist_data()
input_train = input_train[:300]
label_train = label_train[:300]
input_test = input_test[:100]
label_test = label_test[:100]

class Network():
    def __init__(self, layers, dtype=np.float32):
        self.conv_layers = [
            self.ConvLayer(8,3),  # 8 filtres de taille 3x3       `` output 32x32x1 -> 30x30x8
            self.maxPoolingLayer(2), # max pooling de taille 2x2  `` output 30x30x8 -> 15x15x8
            self.ConvLayer(16,3),    #                            `` output 15x15x8 -> 13x13x16
            self.maxPoolingLayer(2) #                             `` output 13x13x16 -> 6x6x16
        ]
        self.layers = layers #dense layers
        self.dtype = dtype
        self.weights = [np.random.randn(layers[i+1], layers[i]).astype(dtype) * np.sqrt(2 / layers[i]) for i in range(len(layers)-1)] # He initialization
        self.biases = [np.zeros(l, dtype=dtype) for l in layers[1:]]
        

    def relu(self, Z):
        return np.maximum(0, Z)
    
    def relu_prime(self, Z):
        return (Z > 0).astype(float) # quand x = 0, ça devrait être undefined, mais il faut faire un choix pratique
    
    def softmax(self, Z):
        exp_z = np.exp(Z)
        return exp_z / (np.sum(exp_z))
    
    def cost_prime(self, predictions, label):
        return predictions - label

    def is_prediction_good(self, output_layer, label):
        return label[np.argmax(output_layer)] == 1
    
    class ConvLayer:
        def __init__(self, num_filters, filter_size):
            self.num_filters = num_filters
            self.filter_size = filter_size
            self.filters = np.random.randn(num_filters, filter_size, filter_size) * np.sqrt(2/ (filter_size * filter_size))
        def forward_convolution(self, input_train):
            self.input = input_train
            height, width, _ = input_train.shape 

            output = np.zeros((height - self.filter_size + 1,
                            width - self.filter_size + 1,
                            self.num_filters))
            
            for f in range(self.num_filters):
                for i in range(height - self.filter_size + 1):
                    for j in range(width - self.filter_size + 1):
                        region = input_train[i:i+self.filter_size, j:j+self.filter_size, 0]
                        output[i, j, f] = np.sum(region * self.filters[f])
            return output
    class maxPoolingLayer: 
        def __init__(self,pool_size):
            self.pool_size = pool_size

        def forward_pooling(self,input,stride):
            height, width, num_filters = input.shape
            output = np.zeros(((height-self.pool_size) // stride + 1, (width-self.pool_size) // stride + 1, num_filters))
            self.max_indices = np.zeros_like(output, dtype=int)
            for filters in range(num_filters): 
                for i in range(0, height - self.pool_size + 1, stride):
                    for j in range(0, width - self.pool_size + 1, stride):
                        region = input[i:i+self.pool_size, j:j+self.pool_size, filters]
                        max_index = region.argmax()
                        output_i, output_j = i // stride, j // stride
                        output[output_i, output_j, filters] = np.max(region)
                        self.max_indices[output_i, output_j, filters] = max_index
            return output
    def foward_through_conv(self, input_train):
        x = self.conv_layers[0].forward_convolution(input_train)
        x= self.relu(x)
        x = self.conv_layers[1].forward_pooling(x, stride=2)
        x = self.conv_layers[2].forward_convolution(x)
        x= self.relu(x)
        x = self.conv_layers[3].forward_pooling(x, stride=2)
        return x
    
    def get_conv_output(self, input_train):
        conv_output = self.foward_through_conv(input_train)
        return conv_output
    
    def forward(self, x, train=False):
        conv_output = self.get_conv_output(x)
        return self.forward_dense(conv_output, train=train)


    def forward_dense(self,conv_output, train=False):
        x= conv_output.flatten() #6x6x16 -> 576 neurons pour la couche d'entrée du réseau de neurones dense
        self.Z = []
        self.activations = []

        Z = [np.zeros(l, dtype=self.dtype) for l in self.layers]
        activations = [np.zeros(l, dtype=self.dtype) for l in self.layers]
        activations[0] = x.flatten()

        for l in range(len(self.layers)-1):
            Z[l] = self.weights[l] @ activations[l] + self.biases[l]
            if l == len(self.layers) - 2:
                activations[l+1] = Z[l] # pas appliquer d'activation aux valeurs de la couche finale
            else:
                activations[l+1] = self.relu(Z[l])

        predictions = self.softmax(activations[-1])

        if train:
            self.Z = Z
            self.activations = activations

        return predictions
    
    def train(self, X_train, X_test, y_train, y_test, batch_size, num_epochs, lr, test_logs=True):
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

                gradient_w = [np.zeros((self.layers[i+1], self.layers[i]), dtype=self.dtype) for i in range(len(self.layers)-1)]
                gradient_b = [np.zeros(l, dtype=self.dtype) for l in self.layers[1:]]

                for x, label in zip(xs, labels):
                    predictions = self.forward(x, True)

                    # Propagation arrière
                    error = self.cost_prime(predictions, label)
                    for l in range(len(self.layers)-2, -1, -1):
                        gradient_w[l] += error[:,None] @ self.activations[l][None,:]
                        gradient_b[l] += error.copy()
                        if l != 0:
                            error = (self.weights[l].T @ error) * self.relu_prime(self.sums[l-1])

                # Descente du gradient
                for i in range(len(self.layers)-1):
                    self.weights[i] -= lr * gradient_w[i] / real_batch_size
                    self.biases[i] -= lr * gradient_b[i] / real_batch_size

            if test_logs:
                print(f"---------- Epoch #{epoch+1} ----------")
                self.test(X_test, y_test)

    def backward_convolution(self, d_output, learning_rate):









    def test(self, X_test, y_test):
        accuracy = 0
        for x, label in zip(X_test, y_test):
            prediction = self.forward(x)
            accuracy += 1 if self.is_prediction_good(prediction, label) else 0
        accuracy /= len(X_test)
        print(f"Model accuracy: {accuracy*100:.2f}%")
    def save_model(self, path):
        data = {}
        for i, W in enumerate(self.weights):
            data[f"W{i}"] = W
        for i, b in enumerate(self.biases):
            data[f"B{i}"] = b
        data["layers"] = self.layers
        np.savez(path, **data)

    def load_model(self, path):
        data = np.load(path)
        self.layers = data["layers"]

        self.weights = []
        self.biases = []

        for i in range(len(self.layers)-1):
            self.weights.append(data[f"W{i}"])
            self.biases.append(data[f"B{i}"])

if __name__ == "__main__":
    X_train, X_test, y_train, y_test = load_mnist_data()
    network = Network([28*28, 128, 32, 10])
    # network.load_model("network/from_scratch/mnist_model.npz")
    network.train(X_train, X_test, y_train, y_test, 128, 10, 0.01)
    network.save_model("network/from_scratch/mnist_model.npz")