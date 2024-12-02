自用 适用于oracle ARM A1 flex 4C24G的实例 嘻嘻

# 在云服务器上用 docker 部署

参考配置：1 核 1GB 内存 ubuntu22 云机器

1. 使用一键脚本安装 docker（https://docs.docker.com/engine/install/ubuntu/）

```
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

2. 配置虚拟内存 swap （例：配置 5G 虚拟内存）

```
sudo fallocate -l 5G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
free -h
```

注意：您可能需要也可能不需要 sudo 来执行 docker 命令。

注意：下面的所有 docker 命令都包含用户名和组 ID。 这些映射到 1001:1001，因为它们是 Oracle 服务器的默认值。 如果您找不到此信息，只需删除它们并在 root 下运行 docker 容器即可。

注意：对于 Windows 服务器，运行 `${pwd}` 而不是 `"$(pwd)"`

3. git clone repo

```
git clone -b inaseg-cloud https://github.com/lovegaoshi/ipynb.git
cd ipynb
```

3a. 安装 docker 镜像

```
sudo docker build -t ipynb-inaseg .
```

OR:

3b. 拉一个预制的 docker 镜像

https://hub.docker.com/repository/docker/gaoshi/ipynb-inaseg/tags?page=1&ordering=last_updated

```
sudo docker pull gaoshi/ipynb-inaseg:nightly
sudo docker tag gaoshi/ipynb-inaseg:nightly ipynb-inaseg
```

4. 用 biliup-rs 登录 b 站账号

```
sudo docker run -v "$(pwd)":/inaseg -u 1001:1001 -it --rm ipynb-inaseg
biliup login
```

```
nano configs/biliWrapper.json
```

```
nano configs/biliWatcher.yaml
```

5.配置

configs/biliWrapper.json：填 b 站投稿的相关信息。格式为：

```
"VUP名": [
        "VUP直播间（转载地址）",
        "视频简介",
        [
            "视频标签"
        ]
    ],
```

configs/biliWatcher.yaml：填监控的相关信息。格式为：

```
- extractor: biliseries
  filter: karaoke
  last_url: true
  url: b站录播合集url
```

6. 使用

切 MP3，适用于自留，做https://steria.vplayer.tk/ 无需登录 b 站账号。

`sudo docker run -v "$(pwd)":/inaseg -u 1001:1001 ipynb-inaseg python /inaseg/inaseg.py --shazam --shazam_multithread=2 --cleanup --outdir=/inaseg --aria=8 --media={回放网址，或本地录播文件地址}`

上传 b 站

`sudo docker run -v "$(pwd)":/inaseg -u 1001:1001 --rm ipynb-inaseg python /inaseg/biliupWrapper.py --media https://www.bilibili.com/video/BV19W4y157Vj/ `

监控 b 站录播合集

`sudo docker run -v "$(pwd)":/inaseg -u 1001:1001 --rm ipynb-inaseg python /inaseg/watcher.py --watch_interval=12800`

# WINDOWS

windows 下也推荐用 docker：https://github.com/lovegaoshi/ipynb/issues/9

# 附加功能

问：更好的系统？ 更多内存？

将 `inaseg.py` 中的 batch_size: `segment_wrapper(media: str, batch_size: int = 32` 从 `32` 更改为较大的值，如 `128` 或 `512`；较大的批次可能会带来 100% 的性能提升。

将媒体滑动窗口大小：“inaseg.py”中的“SEGMENT_THRES = 600”更改为较大的值； 这是在几秒内要处理的最大媒体块。 更大的块将节省磁盘读取。

问：有 CUDA 吗？

改为拉取此图像：

```
sudo docker pull gaoshi/ipynb-inaseg:nightly-gpu
sudo docker tag gaoshi/ipynb-inaseg:nightly-gpu ipynb-inaseg
```

运行 docker 时，添加 `--gpus all`。

要检查 GPU 是否已启用，请运行：

```
sudo docker run -v "$(pwd)":/inaseg -it --rm ipynb-inaseg
python3
import tensorflow as tf
print(tf.config.list_physical_devices('GPU'))
```

请注意，计算机的 CUDA 版本可能需要大于 docker 中的 CUDA 版本 (11.3?)。

问：速度测试

inaseg 获取 1 小时的媒体文件：
Oracle E2.micro(1C2T): ~1hr

AMD Ryzen 3700X(8C16T): ~2min?

NVIDIA 1070, 2070S: < 20s
