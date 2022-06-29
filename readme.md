This is an ina segmenter wrapper can be deployed to any VPS (eg google cloud). can be deployed to your NAS too. even better if you have CUDA.
files in this repo: 
biliup-rs
yt-dlp

to use:
1. use biliup (look up biliup-rs) and generate a login token named cookies.json; put this json file along with all other files in this repo.
2. make an VPS, eg. google cloud compute engine's VPS (i use n2 high mem 4U32G + ubuntu, allowing https and http traffic)
3. install docker as:
Login as super user

    sudo -s

Run the following command to install docker

    sudo apt-get install docker.io

4. docker pull gaoshi/inaseg:gpu
5. upload all files in this repo along with cookies.json into your VPS (eg. the upload button in google cloud ssh's top right corner)
6. put files in 5 in a dir (eg. /home/{your user name}/out)
7. nano biliupWrapper.py and put stream urls in (i have a lot in there)
8. run sudo docker run --rm -it --mount type=bind,source="/home/{your user name}/out",target=/tf/out -u=1001:1002 gaoshi/inaseg:gpu python /tf/out/biliupWrapper.py

4U32G N2 can do 20ms/step; 2070S/2070M/1070 can all do 2ms/step; 840M can do 5ms/step
its definitely cheaper to run your own NAS than VPS
