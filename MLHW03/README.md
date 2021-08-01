# HW03: CNN

Food classification using Convolutional Neural Network.

## ver.0 log

[W pthreadpool-cpp.cc:90] Warning: Leaking Caffe2 thread-pool after fork. (function pthreadpool)

**severe memory leakage**

## ver.1 log

Set
```python
# threads = multiprocessing.cpu_count()
threads = 0

DataLoader(train_set, batch_size=batch_size, shuffle=True, num_workers=threads, pin_memory=True)
```
to prevent memory leakage.

[ Train | 080/080 ] loss = 0.00198, acc = 1.00000
[ Valid | 080/080 ] loss = 3.04568, acc = 0.48516

**overfitting**

score: 

| Private score | Public score |
| ------------- | ------------ |
| 0.51464       | 0.50477      |

## ver.2 log

Add argumentation of training data

```python
train_tfm = transforms.Compose([
    # Resize the image into a fixed shape (height = width = 128)
    transforms.Resize((256, 256)),
    # You may add some transforms here.
    transforms.RandomHorizontalFlip(),
    transforms.RandomResizedCrop(128),
    transforms.ColorJitter(brightness=(0.5, 1.5), contrast=(0.5, 1.5), saturation=(0.5, 1.5), hue=(-0.1, 0.1)),
    transforms.RandomGrayscale(),
    # ToTensor() should be the last one of the transforms.
    transforms.ToTensor(),
    # transforms.Normalize(mean=(0.5, 0.5, 0.5), std=(0.5, 0.5, 0.5)),
])
```

The result is

[ Train | 080/080 ] loss = 1.42164, acc = 0.51562
[ Valid | 080/080 ] loss = 1.42243, acc = 0.51051
Using model with best validation loss 1.263 and accuracy 0.574 to make prediction.

score: 

| Private score | Public score |
| ------------- | ------------ |
| 0.53078       | 0.55256      |

## ver.3 log

Add random rotation in training data transformation

```python
transforms.RandomRotation(degrees=(-45, 45), fill=0),
```

We notice that the model bias occurs after adding data argumentation. Thus, we use 4 convolution layers and 4 fully-connected layers to make model more complex.

The result is

**A: Without dropout**

[ Train | 300/300 ] loss = 0.94674, acc = 0.68399, lr = 1.0000e-05

[ Valid | 300/300 ] loss = 1.36975, acc = 0.63267

Using model with best validation loss 1.23489 and accuracy 0.63864 to make prediction.

score: 

| Private score | Public score |
| ------------- | ------------ |
| 0.58517       | 0.59617      |

**B: With dropout**

[ Train | 912/1000 ] loss = 0.59849, acc = 0.81888, lr = 9.7207e-05

[ Valid | 912/1000 ] loss = 1.26192, acc = 0.70170

Using model with best validation loss 0.96319 and accuracy 0.71051 to make prediction.

score: 

| Private score | Public score |
| ------------- | ------------ |
| 0.71069       | 0.73178      |

