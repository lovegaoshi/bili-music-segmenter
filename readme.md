# 成品

https://www.bilibili.com/video/BV1PL4y1N7VU


# 新新写的windows配置流程

1. 下载并安装 [Mambaforge](https://github.com/mamba-org/mamba/releases)，[windows 用户快速通道](https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-Windows-x86_64.exe)。
2. 打开命令行工具，输入 `conda init powershell`，然后关闭这个窗口，如果出现错误请自行查找解决方案。
3. 按照[这里](https://mirrors.bfsu.edu.cn/help/anaconda/)指引，创建并修改 `.condarc` 文件，更多可以搜索 `conda 换源`。
4. **Nvidia GPU** 用户可选项：（如果没有 Nvidia GPU、GPU 较差、不想使用 GPU 可以跳过此步骤）：
  1. 下载并安装 [CUDA® Toolkit 11.2](https://developer.nvidia.com/cuda-toolkit-archive), 11.2.0 ~ 11.2.2 均可。
  2. 下载 [cudnn 8.1.0](https://developer.nvidia.com/rdp/cudnn-archive)，这里需要注册并登陆 nvidia 账号，注册时的问题可以随便填，选择 `Download cuDNN v8.1.0 (January 26th, 2021), for CUDA 11.0,11.1 and 11.2`，系统对应版本并开始下载。[windows 用户快速通道，需要登陆](https://developer.nvidia.com/compute/machine-learning/cudnn/secure/8.1.0.77/11.2_20210127/cudnn-11.2-windows-x64-v8.1.0.77.zip)。
  3. 将第二步下载完成的压缩包解压，内容复制到 `C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.2\` 中，这个目录在第一步成功执行后才存在。
  4. 验证安装。更多内容可以[参考这里](https://blog.csdn.net/weixin_45048331/article/details/115700427)。
5. 创建一个想要保存切片的目录，例如 `D:\cuts`。
6. 打开命令行工具，进入到这个目录中，分别输入以下命令，以下是配置命令，只需要全部成功执行一次，执行结束后关闭窗口。
```bash
conda create -n cut  # 创建环境
conda activate cut  # 激活环境
conda install jupyter ffmpeg # 安装在线编辑器、视频处理工具 ffmpeg
pip config set global.index-url https://mirrors.bfsu.edu.cn/pypi/web/simple # 换成国内下载地址
pip install tensorflow-gpu==2.10.1
pip install inaSpeechSegmenter 'https://github.com/Numenorean/ShazamAPI/archive/master.zip' loguru zhconv # 国内 https://github.com/Numenorean/ShazamAPI/archive/master.zip 不行就换成 https://ghproxy.com/github.com/Numenorean/ShazamAPI/archive/master.zip
```

# 新写的windows配置流程

首先装[64位的miniconda](https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe)

在d盘新建一个文件夹inaseg
下载[yt-dlp](https://github.com/yt-dlp/yt-dlp/releases)或者[点这个220901的版本](https://github.com/yt-dlp/yt-dlp/releases/download/2022.09.01/yt-dlp.exe)放进去

（可选）下载[aria2c](https://github.com/aria2/aria2/releases/)加速下载

解压本repo的所有文件放到这个文件夹里；目前文件夹如图

![folder content](https://raw.githubusercontent.com/lovegaoshi/ipynb/main/src/dir_structure.PNG "folder contnet")

点开始->anaconda

输入D:

输入cd inaseg

输入 conda create -n cut python=3.8

输入 conda activate cut

输入 conda install ffmpeg

输入 pip install inaspeechsegmenter shazamapi jupyter notebook filelock pyyaml -i https://pypi.tuna.tsinghua.edu.cn/simple

（后面的清华大学那一坨是国内pip镜像站；非国内的可以删了）

输入 jupyter notebook

打开inaWrapper.ipynb

按红字提示，一路点下去。里面演示的是桃老师的直播回放

有N卡的朋友：装CUDA；conda install cudnn；pip install tensorflow-gpu --upgrade 调用n卡加速


# inaseg_google_colab.ipynb

colab 页面截图:

<img alt="colab" src="https://user-images.githubusercontent.com/35656321/222389469-0de96336-c7e6-4fb5-9c01-6857a01fd814.png" width="30%">

## 在 colab 运行

1. 首先你需要有个谷歌账号，并且你可以正常访问谷歌。
2. 打开 [colab](https://colab.research.google.com/)
  1. 选择 `GitHub`
  2. 输入 https://github.com/lovegaoshi/ipynb/blob/google-cloud/inaseg_google_colab.ipynb
  3. 点击输入框旁边的搜索按钮。（不要点下面的新建！）
3. 第一个格子直接执行。
4. 第二个替换成自己想要的录播下载方式。**请从B站（不推荐）、Youtube、谷歌网盘、Onedrive等直接下载，不要上传，速度很慢！**
  1. B站下载可以使用 [BBDown](https://github.com/nilaoda/BBDown) **等**工具，注意一定要想办法登陆账号或者上传账号配置文件，否则只能下载 360P 以下的视频！
  2. Youtube 下载可以使用 [you-get](https://github.com/soimort/you-get) **等**工具，如果无法下载请自行查找其他工具。
  3. 谷歌网盘、Onedrive 等，推荐使用 [Alist](https://github.com/alist-org/alist)、[cloudreve](https://github.com/cloudreve/Cloudreve) 等网盘索引工具获取到直链后，使用 aria2 下载。也可以使用 rclone 从网盘复制。如果录播在的谷歌网盘和 colab 同账号，直接挂载网盘即可，不必再次下载。
5. 第三个格子直接执行。
6. 将第四个格子的 `raw_file_path = '/content/10850238.mp4'` 修改为自己在第4步中下载的文件位置（在左侧文件浏览器中，右键-复制绝对路径。）
7. 运行第四个格子，如果出现问题，请检查录播的完整性，或者把文件名特殊字符删掉再次尝试。
8. 分割成功，但是无法识别歌名的切片在 `/content/convert2music` 文件夹，识别成功的切片在 `'/content/recognized'` 文件夹。
9. **请不要直接从 colab 下载文件**。运行第五个格子，将切片文件复制到自己的谷歌网盘中，然后从谷歌网盘下载（速度更快）。注意谷歌硬盘容量不要超标。

## 在本地运行

`inaseg_google_colab.ipynb` 目前也支持在本地运行，不过由于个人讨厌B站压缩视频，因此此笔记本只有 `切片-识别` 功能，没有 `上传到B站投稿` 功能。
1. 按照 `新新写的windows配置流程` 安装配置环境。
2. 下载 inaseg_google_colab.ipynb 到配置环境步骤5 中的目录，这里是 `D:\cuts\inaseg_google_colab.ipynb`
3. 命令行工具，进入到这个目录中，输入以下命令（每次都需要），会自动打开浏览器页面：
```bash
conda activate cut
jupyter notebook
```
4. 浏览器页面中选择 `inaseg_google_colab.ipynb`，则可以看到和 colab 打开笔记本后相同的内容。
5. **第一个格子不用执行，直接删除。**（对的，本地到现在的步骤 = colab 打开链接执行第一个格子即可，气不气?）
6.用任何方式将录播下载到本地，不必一定通过执行第二个格子下载的方式。
7. 第三个格子直接执行。
8. 将第四个格子的 `raw_file_path = '/content/10850238.mp4'` 修改为自己本地文件位置; `seg_out_dir = r'/content/convert2music'` 修改为本地目录，例如 `seg_out_dir = r'./convert2music'`;`recognized_dir = r'/content/recognized'` 修改为本地目录，例如 `recognized_dir = r'./recognized'`;
9. 运行第四个格子，如果出现问题，请检查录播的完整性，或者把文件名特殊字符删掉再次尝试。
10. 运行结束后切片就在对应目录中。**第五个格子不用执行，直接删除。**


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
