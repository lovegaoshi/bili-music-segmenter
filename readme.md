
# 在云服务器上用docker部署
参考配置：1核1GB内存ubuntu云机器

1. 使用一键脚本安装docker
https://docs.docker.com/engine/install/ubuntu/

curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

2. 配置虚拟内存swap
以5GB 虚拟内存为参考：
sudo fallocate -l 5G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
free -h

3. 安装docker镜像
下载
wget -q -O - "https://github.com/ForgQi/biliup-rs/releases/download/v0.1.15/biliupR-v0.1.15-x86_64-linux.tar.xz" | tar xJ

cd inaseg
sudo docker compose up

4. 测试
python inaseg.py --shazam --media=https://www.bilibili.com/video/BV17R4y117mn/ --shazam_multithread=2 --cleanup

∞. 处理速度
1核1GB： 250ms处理时间/0.8s视频长度
4核16GB：~100ms
GTX 840M: 20ms
1070: 2-3ms
2070s: 2ms


wget -q -O - "https://github.com/ForgQi/biliup-rs/releases/download/v0.1.15/biliupR-v0.1.15-x86_64-linux.tar.xz" | tar xJ