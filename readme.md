# 成品

https://www.bilibili.com/video/BV1PL4y1N7VU

https://www.bilibili.com/video/BV1vS4y1e7gc

https://www.bilibili.com/video/BV1jY4y1s7mq

https://www.bilibili.com/video/BV1HB4y1S7HX

# Colab
you can run this in Colab with free GPU resources! although colab's download speed is quite bad at 300kB/s. open this file:
https://github.com/lovegaoshi/ipynb/blob/google-cloud/inaseg_google_colab.ipynb

# Docker
you can run this with docker (can do with gpu enabled)! just do docker pull gaoshi/inaseg:gpu.

# Dependencies

FFMPEG: https://ffmpeg.org/download.html

anaconda (not necessary but you really should): https://www.anaconda.com/

BILIBILI cmdline upload: https://github.com/ForgQi/biliup-rs/releases

CUDA: its a long list but its as simple as downloading a CUDA installer, a CuDNN installer, copying some files over and a reboot. https://medium.com/geekculture/install-cuda-and-cudnn-on-windows-linux-52d1501a8805

Inaspeech and ShazamAPI (through pip)

and finally set up the folder like this (or add PATH, whatever your choices are):

# Usage

first configure BILIBILI cmdline upload by following the instructions @ https://github.com/ForgQi/biliup-r

then open anaconda, make an env and go to the folder and run jupyter notebook:

for the very first time, run the first cell to install inaspeech and shazamapi;

configure some things in the 2nd cell, and click run.
