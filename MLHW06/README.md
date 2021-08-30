# **Homework 6 - Generative Adversarial Network**

Reference: https://colab.research.google.com/github/ga642381/ML2021-Spring/blob/main/HW06/HW06.ipynb#scrollTo=oZ-C2Dgetg37

## ver.0 log

Set num_workers=0

Change qqdm to tqdm

Save the checkpoints of the models at every epochs

Handle SIGINT to control early stop

If the checkpoints exist, asks if you want to load the last model

Use plt.draw to prevent blocking the process when showing the image.

## ver.1 log

Tune:
batch_size = 16
n_epoch = 1000
n_critic = 1
