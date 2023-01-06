# 在云服务器上用docker部署
参考配置：1核1GB内存ubuntu云机器

1. 使用一键脚本安装docker（https://docs.docker.com/engine/install/ubuntu/）

curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

2. 配置虚拟内存swap （例：配置5G虚拟内存）
sudo fallocate -l 5G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
free -h

3. 安装docker镜像
git clone -b inaseg-cloud https://github.com/lovegaoshi/ipynb.git
cd ipynb
sudo docker compose up

4. 使用
sudo docker run -v "$(pwd)":/inaseg -u 1001:1001 ipynb-inaseg python inaseg/inaseg.py --shazam --shazam_multithread=2 --cleanup --outdir=/inaseg --aria=8 --media={回放网址，或本地录播文件地址}

处理速度特别慢是因为配置答辩；正常6核12线程的机器比这个快10倍，落后n卡（GTX840M）比这个快40倍，稍落后n卡（1070）比这个快80倍

wget -q -O - "https://github.com/ForgQi/biliup-rs/releases/download/v0.1.15/biliupR-v0.1.15-x86_64-linux.tar.xz" | tar xJ