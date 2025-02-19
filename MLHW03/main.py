"""
https://colab.research.google.com/github/ga642381/ML2021-Spring/blob/main/HW03/HW03.ipynb#scrollTo=3t2q2Th85ZUE
Homework 3 - Convolutional Neural Network
This is the example code of homework 3 of the machine learning course by Prof. Hung-yi Lee.
In this homework, you are required to build a convolutional neural network for image classification, possibly with some advanced training tips.

There are three levels here:
Easy: Build a simple convolutional neural network as the baseline. (2 pts)
Medium: Design a better architecture or adopt different data augmentations to improve the performance. (2 pts)
Hard: Utilize provided unlabeled data to obtain better results. (2 pts)
"""

'''
Import Packages
First, we need to import packages that will be used later.
In this homework, we highly rely on torchvision, a library of PyTorch.
'''
# Import necessary packages.
import numpy as np
import torch
import torch.nn as nn
import torchvision.transforms as transforms
from PIL import Image
# "ConcatDataset" and "Subset" are possibly useful when doing semi-supervised learning.
from torch.utils.data import ConcatDataset, DataLoader, Subset
from torchvision.datasets import DatasetFolder

# This is for the progress bar.
from tqdm.auto import tqdm

# This is for configuring CPU threads
import multiprocessing

# This is for garbage collection
import gc

import os


class Bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


'''
Dataset, Data Loader, and Transforms
Torchvision provides lots of useful utilities for image preprocessing, data wrapping as well as data augmentation.
Here, since our data are stored in folders by class labels, we can directly apply torchvision.datasets.DatasetFolder for wrapping data without much effort.
Please refer to PyTorch official website for details about different transforms.
'''
# It is important to do data augmentation in training.
# However, not every augmentation is useful.
# Please think about what kind of augmentation is helpful for food recognition.
train_tfm = transforms.Compose([
    # Resize the image into a fixed shape (height = width = 128)
    transforms.Resize((256, 256)),
    # You may add some transforms here.
    transforms.RandomHorizontalFlip(),
    transforms.RandomResizedCrop(128),
    transforms.RandomRotation(degrees=(-45, 45), fill=0),
    transforms.ColorJitter(brightness=(0.5, 1.5), contrast=(0.5, 1.5), saturation=(0.5, 1.5), hue=(-0.1, 0.1)),
    transforms.RandomGrayscale(),
    # ToTensor() should be the last one of the transforms.
    transforms.ToTensor(),
    # transforms.Normalize(mean=(0.5, 0.5, 0.5), std=(0.5, 0.5, 0.5)),
])

# We don't need augmentations in testing and validation.
# All we need here is to resize the PIL image and transform it into Tensor.
test_tfm = transforms.Compose([
    transforms.Resize((128, 128)),
    transforms.ToTensor(),
    # transforms.Normalize(mean=(0.5, 0.5, 0.5), std=(0.5, 0.5, 0.5)),
])

# Batch size for training, validation, and testing.
# A greater batch size usually gives a more stable gradient.
# But the GPU memory is limited, so please adjust it carefully.
batch_size = 32
# threads = multiprocessing.cpu_count()
threads = 0

# Construct datasets.
# The argument "loader" tells how torchvision reads the data.
train_set = DatasetFolder("./food-11/training/labeled", loader=lambda x: Image.open(x), extensions="jpg", transform=train_tfm)
valid_set = DatasetFolder("./food-11/validation", loader=lambda x: Image.open(x), extensions="jpg", transform=test_tfm)
# unlabeled_set = DatasetFolder("./food-11/training/unlabeled", loader=lambda x: Image.open(x), extensions="jpg", transform=train_tfm)
test_set = DatasetFolder("./food-11/testing", loader=lambda x: Image.open(x), extensions="jpg", transform=test_tfm)

# Construct data loaders.
train_loader = DataLoader(train_set, batch_size=batch_size, shuffle=True, num_workers=threads, pin_memory=True)
valid_loader = DataLoader(valid_set, batch_size=batch_size, shuffle=True, num_workers=threads, pin_memory=True)
test_loader = DataLoader(test_set, batch_size=batch_size, shuffle=False)

'''
Model
The basic model here is simply a stack of convolutional layers followed by some fully-connected layers.
Since there are three channels for a color image (RGB), the input channels of the network must be three. In each convolutional layer, typically the channels of inputs grow, while the height and width shrink (or remain unchanged, according to some hyperparameters like stride and padding).
Before fed into fully-connected layers, the feature map must be flattened into a single one-dimensional vector (for each image). These features are then transformed by the fully-connected layers, and finally, we obtain the "logits" for each class.

WARNING -- You Must Know
You are free to modify the model architecture here for further improvement. However, if you want to use some well-known architectures such as ResNet50, please make sure NOT to load the pre-trained weights. Using such pre-trained models is considered cheating and therefore you will be punished. Similarly, it is your responsibility to make sure no pre-trained weights are used if you use torch.hub to load any modules.
For example, if you use ResNet-18 as your model:
model = torchvision.models.resnet18(pretrained=False) → This is fine.
model = torchvision.models.resnet18(pretrained=True) → This is NOT allowed.
'''
# the path where checkpoint saved
model_path = './model.ckpt'


class Classifier(nn.Module):
    def __init__(self):
        super(Classifier, self).__init__()
        # The arguments for commonly used modules:
        # torch.nn.Conv2d(in_channels, out_channels, kernel_size, stride, padding)
        # torch.nn.MaxPool2d(kernel_size, stride, padding)

        # input image size: [#, 3, 128, 128] (#: Number of inputs)
        self.cnn_layers = nn.Sequential(
            nn.Conv2d(3, 64, 3, 1, 1),  # [#, 64, 128, 128]
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(2, 2, 0),  # [#, 64, 64, 64]

            nn.Conv2d(64, 128, 3, 1, 1),  # [#, 128, 64, 64]
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.MaxPool2d(2, 2, 0),  # [#, 128, 32, 32]

            nn.Conv2d(128, 256, 3, 1, 1),  # [#, 256, 32, 32]
            nn.BatchNorm2d(256),
            nn.ReLU(),
            nn.Dropout(p=0.15),
            nn.MaxPool2d(2, 2, 0),  # [#, 256, 16, 16]

            nn.Conv2d(256, 512, 3, 1, 1),  # [#, 512, 16, 16]
            nn.BatchNorm2d(512),
            nn.ReLU(),
            nn.Dropout(p=0.15),
            nn.MaxPool2d(2, 2, 0),  # [#, 512, 8, 8]
        )
        self.fc_layers = nn.Sequential(  # fc = fully-connected
            nn.Linear(512 * 8 * 8, 4096),  # [#, 4096]
            nn.ReLU(),
            nn.Dropout(p=0.15),
            nn.Linear(4096, 1024),  # [#, 1024]
            nn.ReLU(),
            nn.Dropout(p=0.15),
            nn.Linear(1024, 256),  # [#, 1024]
            nn.ReLU(),
            nn.Linear(256, 256),  # [#, 256]
            nn.ReLU(),
            nn.Linear(256, 11)  # [#, 11]
        )

    def forward(self, x):
        # input (x): [batch_size, 3, 128, 128]
        # output: [batch_size, 11]

        # Extract features by convolutional layers.
        x = self.cnn_layers(x)

        # The extracted feature map must be flatten before going to fully-connected layers.
        x = x.flatten(1)  # [#, 16384]

        # The features are transformed by fully-connected layers to obtain the final logits.
        x = self.fc_layers(x)
        return x


'''
Training
You can finish supervised learning by simply running the provided code without any modification.
The function "get_pseudo_labels" is used for semi-supervised learning. It is expected to get better performance if you use unlabeled data for semi-supervised learning. However, you have to implement the function on your own and need to adjust several hyperparameters manually.
For more details about semi-supervised learning, please refer to Prof. Lee's slides.
Again, please notice that utilizing external data (or pre-trained model) for training is prohibited.
'''


def get_pseudo_labels(dataset, model, threshold=0.65):
    # This functions generates pseudo-labels of a dataset using given model.
    # It returns an instance of DatasetFolder containing images whose prediction confidences exceed a given threshold.
    # You are NOT allowed to use any models trained on external data for pseudo-labeling.
    device = "cuda" if torch.cuda.is_available() else "cpu"
    labels = []
    # Construct a data loader.
    data_loader = DataLoader(dataset, batch_size=batch_size, shuffle=False)

    # Make sure the model is in eval mode.
    model.eval()
    # Define softmax function.
    softmax = nn.Softmax(dim=-1)
    # Iterate over the dataset by batches.
    print("\ngenerate pseudo labels...")
    # t = 0
    for batch in tqdm(data_loader):
        # t += 1
        # if t > 10:
        #     break
        img, label = batch

        # Forward the data
        # Using torch.no_grad() accelerates the forward process.
        with torch.no_grad():
            logits = model(img.to(device))

        # Obtain the probability distributions by applying softmax on logits.
        probs = softmax(logits)
        for p in probs:
            if torch.max(p) > threshold:
                labels.append(torch.argmax(p).cpu().numpy().item())
            else:
                labels.append(-1)

    print("\ndata set len", len(dataset.samples))
    print("label len", len(labels))
    print("#############################################")
    for i, sample in enumerate(dataset.samples):
        try:
            if labels[i] == -1:
                continue
            else:
                dataset.samples[i] = (sample[0], labels[i])
        except:
            dataset.samples.remove(sample)
    rm_list = []
    for i, sample in enumerate(dataset.samples):
        if i >= len(labels) or labels[i] == -1:
            rm_list.append(sample)
    # print(rm_list)
    for i in rm_list:
        dataset.samples.remove(i)
    # print("#####", dataset.samples)

    # ---------- TODO ----------
    # Filter the data and construct a new dataset.

    # # Turn off the eval mode.
    model.train()
    return dataset


# "cuda" only when GPUs are available.
device = "cuda" if torch.cuda.is_available() else "cpu"

# Initialize a model, and put it on the device specified.
model = Classifier().to(device)
model.device = device

# For the classification task, we use cross-entropy as the measurement of performance.
criterion = nn.CrossEntropyLoss()

# The number of training epochs.
n_epochs = 10000  # n_epochs must greater than 1
start_lr = 1e-3
end_lr = 1e-5

# Whether to do semi-supervised learning.
do_semi = True
best_loss = 10000000.0
best_acc = 0.0

if os.path.isfile(model_path):
    print(f"{model_path} exists, do you want to load the last model? (y/n)")
    yn = input()
    if yn == "y" or yn == "Y":
        print("Loading last model")
        model.load_state_dict(torch.load(model_path), strict=False)
try:
    for epoch in range(n_epochs):
        m = (end_lr - start_lr) / (n_epochs - 1)
        k = start_lr - m
        learning_rate = (m * (epoch + 1) + k)  # Adaptive learning rate
        # Initialize optimizer, you may fine-tune some hyperparameters such as learning rate on your own.
        optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate, weight_decay=1e-5)

        # ---------- TODO ----------
        # In each epoch, relabel the unlabeled dataset for semi-supervised learning.
        # Then you can combine the labeled dataset and pseudo-labeled dataset for the training.
        if do_semi:
            unlabeled_set = DatasetFolder("./food-11/training/unlabeled", loader=lambda x: Image.open(x), extensions="jpg", transform=train_tfm)
            # Obtain pseudo-labels for unlabeled data using trained model.
            pseudo_set = get_pseudo_labels(unlabeled_set, model)

            # Construct a new dataset and a data loader for training.
            # This is used in semi-supervised learning only.
            concat_dataset = ConcatDataset([train_set, pseudo_set])
            train_loader = DataLoader(concat_dataset, batch_size=batch_size, shuffle=True, num_workers=threads, pin_memory=True)

        # ---------- Training ----------
        # Make sure the model is in train mode before training.
        model.train()

        # These are used to record information in training.
        train_loss = []
        train_accs = []

        # Iterate the training set by batches.
        for batch in tqdm(train_loader):
            # A batch consists of image data and corresponding labels.
            imgs, labels = batch

            # Forward the data. (Make sure data and model are on the same device.)
            logits = model(imgs.to(device))

            # Calculate the cross-entropy loss.
            # We don't need to apply softmax before computing cross-entropy as it is done automatically.
            loss = criterion(logits, labels.to(device))

            # Gradients stored in the parameters in the previous step should be cleared out first.
            optimizer.zero_grad()

            # Compute the gradients for parameters.
            loss.backward()

            # Clip the gradient norms for stable training.
            grad_norm = nn.utils.clip_grad_norm_(model.parameters(), max_norm=10)

            # Update the parameters with computed gradients.
            optimizer.step()

            # Compute the accuracy for current batch.
            acc = (logits.argmax(dim=-1) == labels.to(device)).float().mean()

            # Record the loss and accuracy.
            train_loss.append(loss.detach().item())  # add detach()
            train_accs.append(acc)

        # The average loss and accuracy of the training set is the average of the recorded values.
        train_loss = sum(train_loss) / len(train_loss)
        train_acc = sum(train_accs) / len(train_accs)

        # Print the information.
        print(f"\n[ Train | {epoch + 1:03d}/{n_epochs:03d} ] loss = {train_loss:.5f}, acc = {train_acc:.5f}, lr = {learning_rate:.4e}")

        # ---------- Validation ----------
        # Make sure the model is in eval mode so that some modules like dropout are disabled and work normally.
        model.eval()

        # These are used to record information in validation.
        valid_loss = []
        valid_accs = []

        # Iterate the validation set by batches.
        for batch in tqdm(valid_loader):
            # A batch consists of image data and corresponding labels.
            imgs, labels = batch

            # We don't need gradient in validation.
            # Using torch.no_grad() accelerates the forward process.
            with torch.no_grad():
                logits = model(imgs.to(device))

            # We can still compute the loss (but not the gradient).
            loss = criterion(logits, labels.to(device))

            # Compute the accuracy for current batch.
            acc = (logits.argmax(dim=-1) == labels.to(device)).float().mean()

            # Record the loss and accuracy.
            valid_loss.append(loss.detach().item())  # add detach()
            valid_accs.append(acc)

        # The average loss and accuracy for entire validation set is the average of the recorded values.
        valid_loss = sum(valid_loss) / len(valid_loss)
        valid_acc = sum(valid_accs) / len(valid_accs)

        # Print the information.
        print(f"\n[ Valid | {epoch + 1:03d}/{n_epochs:03d} ] loss = {valid_loss:.5f}, acc = {valid_acc:.5f}")

        # if the model improves, save a checkpoint at this epoch
        if best_loss > valid_loss:
            best_loss = valid_loss
            best_acc = valid_acc
            print(f"\n{Bcolors.WARNING}Saving model with validation loss {best_loss:.5f} and accuracy {best_acc:.5f}{Bcolors.ENDC}")
            torch.save(model.state_dict(), model_path)

        # gc.collect()  # Add garbage collection for each iteration of training loop
except KeyboardInterrupt:
    print("stop!!!")
'''
Testing
For inference, we need to make sure the model is in eval mode, and the order of the dataset should not be shuffled ("shuffle=False" in test_loader).
Last but not least, don't forget to save the predictions into a single CSV file. The format of CSV file should follow the rules mentioned in the slides.

WARNING -- Keep in Mind
Cheating includes but not limited to:
1. using testing labels,
2. submitting results to previous Kaggle competitions,
3. sharing predictions with others,
4. copying codes from any creatures on Earth,
5. asking other people to do it for you.
Any violations bring you punishments from getting a discount on the final grade to failing the course.

It is your responsibility to check whether your code violates the rules. When citing codes from the Internet, you should know what these codes exactly do. You will NOT be tolerated if you break the rule and claim you don't know what these codes do.
'''
# Make sure the model is in eval mode.
# Some modules like Dropout or BatchNorm affect if the model is in training mode.
model = Classifier().to(device)
model.load_state_dict(torch.load(model_path))
model.eval()

# Initialize a list to store the predictions.
predictions = []

# Iterate the testing set by batches.
for batch in tqdm(test_loader):
    # A batch consists of image data and corresponding labels.
    # But here the variable "labels" is useless since we do not have the ground-truth.
    # If printing out the labels, you will find that it is always 0.
    # This is because the wrapper (DatasetFolder) returns images and labels for each batch,
    # so we have to create fake labels to make it work normally.
    imgs, labels = batch

    # We don't need gradient in testing, and we don't even have labels to compute loss.
    # Using torch.no_grad() accelerates the forward process.
    with torch.no_grad():
        logits = model(imgs.to(device))

    # Take the class with greatest logit as prediction and record it.
    predictions.extend(logits.argmax(dim=-1).cpu().numpy().tolist())

# Save predictions into the file.
with open("predict.csv", "w") as f:
    # The first row must be "Id, Category"
    print('Using model with best validation loss {:.5f} and accuracy {:.5f} to make prediction.'.format(best_loss, best_acc))
    f.write("Id,Category\n")

    # For the rest of the rows, each image id corresponds to a predicted class.
    for i, pred in enumerate(predictions):
        f.write(f"{i},{pred}\n")
    print("The prediction has been written successfully.")
