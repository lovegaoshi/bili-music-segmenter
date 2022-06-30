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

    sudo apt-get update

    sudo apt-get install docker.io

4. docker pull:

    docker pull gaoshi/inaseg:gpu
    
5. upload all files in this repo along with cookies.json into your VPS somehow (eg. the upload button in google cloud ssh's top right corner)
6. chmod 777 both ./biliup and ./yt-dlp; otherwise there will be permission issues
7. nano biliupWrapper.py and configure stream urls in and youtuber tags 
8. make sure to run in a screen! then

    sudo docker run --rm -it --mount type=bind,source="/home/{your user name}",target=/tf/out -u=1001:1002 gaoshi/inaseg:gpu python /tf/out/biliupWrapper.py

note the -u ID needs to be right (or run as root?), otherwise you'll have permission issues

N2-highmem-4 can do 20ms/step; 2070S/2070M/1070 can all do 2ms/step; 840M can do 5ms/step (batch size 32)
N2-hgihmem-4 is $8 per day?
32G RAM is quite necessary, 4 core is not
