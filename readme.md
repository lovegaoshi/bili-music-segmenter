# 成品

https://www.bilibili.com/video/BV1PL4y1N7VU


# 新写的windows配置流程

首先装[64位的miniconda](https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe)

在d盘新建一个文件夹inaseg

下载[ffmpeg](https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-full.7z)，把bin/里的ffmpeg.exe等文件解压放进去

下载[yt-dlp](https://github.com/yt-dlp/yt-dlp/releases)或者[点这个220901的版本](https://github.com/yt-dlp/yt-dlp/releases/download/2022.09.01/yt-dlp.exe)放进去

（可选）下载[aria2c](https://github.com/aria2/aria2/releases/)加速下载

解压本repo的所有文件放到这个文件夹里；目前文件夹如图

![folder content](https://raw.githubusercontent.com/lovegaoshi/ipynb/main/src/dir_structure.PNG "folder contnet")

点开始->anaconda

输入D:

输入cd inaseg

输入 conda create -n inaseg python=3.8

输入 conda activate inaseg

输入 pip install inaspeechsegmenter shazamapi jupyter notebook filelock pyyaml -i https://pypi.tuna.tsinghua.edu.cn/simple

（后面的清华大学那一坨是国内pip镜像站；非国内的可以删了）

输入 jupyter notebook

打开inaWrapper.ipynb

按红字提示，一路点下去。里面演示的是桃老师的直播回放

有N卡的朋友：装CUDA；conda install cudnn；pip install tensorflow-gpu --upgrade 调用n卡加速


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
