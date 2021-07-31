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

Add augementation of training data

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

