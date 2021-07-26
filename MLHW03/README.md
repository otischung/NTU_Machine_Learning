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

