# 在云服务器上用docker部署

参考配置：1核1GB内存ubuntu22云机器

1. 使用一键脚本安装docker（https://docs.docker.com/engine/install/ubuntu/）
```
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

2. 配置虚拟内存swap （例：配置5G虚拟内存）
```
sudo fallocate -l 5G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
free -h
```

NOTE: you may or may not need sudo to perform docker commands.

NOTE: all docker commands below contains the user name and group id. these are mapped to 1001:1001 as they are the defaults for oracle servers. If you cannot locate this information, simply remove them and run the docker container under root. 

NOTE: for windows servers, run `${pwd}` instead of `"$(pwd)"`

3. git clone repo
```
git clone -b inaseg-cloud https://github.com/lovegaoshi/ipynb.git
cd ipynb
```

3a. 安装docker镜像
```
sudo docker build .
```
OR:

3b. pull a premade docker镜像

https://hub.docker.com/repository/docker/gaoshi/ipynb-inaseg/tags?page=1&ordering=last_updated

```
sudo docker pull gaoshi/ipynb-inaseg:nightly
sudo docker tag gaoshi/ipynb-inaseg:nightly ipynb-inaseg
```

4. 用biliup-rs登录b站账号
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

configs/biliWrapper.json：填b站投稿的相关信息。格式为：
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

切MP3，适用于自留，做https://steria.vplayer.tk/ 无需登录b站账号。

`sudo docker run -v "$(pwd)":/inaseg -u 1001:1001 ipynb-inaseg python /inaseg/inaseg.py --shazam --shazam_multithread=2 --cleanup --outdir=/inaseg --aria=8 --media={回放网址，或本地录播文件地址}`

上传b站

`sudo docker run -v "$(pwd)":/inaseg -u 1001:1001 --rm ipynb-inaseg python /inaseg/biliupWrapper.py --media https://www.bilibili.com/video/BV19W4y157Vj/ `

监控b站录播合集

`sudo docker run -v "$(pwd)":/inaseg -u 1001:1001 --rm ipynb-inaseg python /inaseg/BiliWatcher.py --watch_interval=12800`

7. Extras

Q: better system? more RAM?

change batch_size: `segment_wrapper(media: str, batch_size: int = 32` in `inaseg.py` from `32` to something large like `128` or `512`; a larger batch may have 100% performance increase.

change media sliding window size: `SEGMENT_THRES = 600` in `inaseg.py` to something large; this is the largest media chunk to be processed in seconds. a larger chunk will save disk read.

Q: has CUDA?

pull this image instead:

```
sudo docker pull gaoshi/ipynb-inaseg:nightly-gpu
sudo docker tag gaoshi/ipynb-inaseg:nightly-gpu ipynb-inaseg
```

when running docker, add `--gpus all`.

to check if GPU is enabled, run:

```
sudo docker run -v "$(pwd)":/inaseg -it --rm ipynb-inaseg
python3
import tensorflow as tf
print(tf.config.list_physical_devices('GPU'))
```

note that your computer's CUDA version might need to be larger than the CUDA version in docker. 

Q: speed tests

inaseg for an 1 hour media file: 

Oracle E2.micro(1C2T): ~1hr

AMD Ryzen 3700X(8C16T): ~2min?

NVIDIA 1070, 2070S: < 20s
