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
4. 安装docker镜像
```
git clone -b inaseg-cloud https://github.com/lovegaoshi/ipynb.git
cd ipynb
sudo docker compose up
```

3b. 用biliup-rs登录b站账号
```sudo docker run -v "$(pwd)":/inaseg -u 1001:1001 -it --rm ipynb-inaseg
./biliup login
配置b站上传视频信息
nano configs/biliWrapper.json
nano configs/biliWatcher.yaml
```


4. 使用<br />
切MP3，适用于自留，做https://steria.vplayer.tk/ 无需登录b站账号。<br />
`sudo docker run -v "$(pwd)":/inaseg -u 1001:1001 ipynb-inaseg python inaseg/inaseg.py --shazam --shazam_multithread=2 --cleanup --outdir=/inaseg --aria=8 --media={回放网址，或本地录播文件地址}` <br />
上传b站<br />
`sudo docker run -v "$(pwd)":/inaseg -u 1001:1001 --rm ipynb-inaseg python /inaseg/biliupWrapper.py --media` https://www.bilibili.com/video/BV19W4y157Vj/<br />
监控b站录播合集<br />
`sudo docker run -v "$(pwd)":/inaseg -u 1001:1001 --rm ipynb-inaseg python /inaseg/BiliWatcher.py --watch_interval=0`<br />

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
