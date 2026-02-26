import numpy as np 
from PIL import Image 

import torch
from torch import nn
import torch.nn.functional as F 
import torch.optim as optim

import torchvision
import torchvision.transforms as T

transform = T.Compose([
    T.Grayscale(num_output_channels=1),  
    T.ToTensor(),
    T.Normalize((0.5,), (0.5,))  
])