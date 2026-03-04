import numpy as np
from PIL import Image, ImageOps
import random
import os
#to play code :   py -m network.experimental.from_scratch_CNN.from_scratch

# Base path from your screenshot
base_path = "dataset/dataset-data/training-data/"

# --- NEW: Initialize storage for your CNN data ---
all_images = []
all_labels = []

# 1. Loop through category folders (0, 1, 2, 3, 4)
for label_folder in os.listdir(base_path):
    category_path = os.path.join(base_path, label_folder)
    
    if not os.path.isdir(category_path):
        continue

    # 2. Loop through actual images in those folders
    for image_name in os.listdir(category_path):
        full_path = os.path.join(category_path, image_name)
        
        img = Image.open(full_path)
        img = img.resize((32, 32), resample=Image.BILINEAR)
        img = ImageOps.grayscale(img)

        # Data Augmentation (Rotation + Translation)
        angle = random.uniform(-15, 15)
        tx = random.uniform(-0.1, 0.1) * 32
        ty = random.uniform(-0.1, 0.1) * 32

        img = img.rotate(
            angle, 
            resample=Image.BILINEAR, 
            expand=False, 
            translate=(tx, ty),
            fillcolor=0
        )

        # 3. NumPy Processing
        img_np = np.array(img).astype(np.float32) / 255.0
            
        # Normalizing to range [-1, 1]
        img_np = (img_np - 0.5) / 0.5
            
        # --- NEW: Append to our dataset ---
        # We add a channel dimension so shape becomes (32, 32, 1)
        img_np = np.expand_dims(img_np, axis=-1) 
            
        all_images.append(img_np)
        all_labels.append(int(label_folder)) # Assumes folder names are 0, 1, 2...

# 4. Convert lists to NumPy arrays and shuffle
X = np.array(all_images)
y = np.array(all_labels)

indices = np.arange(len(X))
np.random.shuffle(indices)

X = X[indices]
y = y[indices]

split = int(0.8 * len(X))

train_data = X[:split]
train_labels = y[:split]

test_data = X[split:]
test_labels = y[split:]

num_classes = len(np.unique(y))

y_train = np.eye(num_classes)[train_labels]   # One-hot encoding pour bien marcher avec softmax et cross-entropy
y_test = np.eye(num_classes)[test_labels]