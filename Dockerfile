FROM tensorflow/tensorflow:2.18.0
RUN sudo apt-get update --allow-insecure-repositories
RUN sudo apt-get -y --allow-unauthenticated install ffmpeg aria2 wget nano git
WORKDIR /inaseg
RUN git clone https://github.com/lovegaoshi/inaSpeechSegmenter.git
RUN cd inaSpeechSegmenter; pip install .
COPY ./requirements.txt /inaseg/requirements.txt
RUN pip3 install -r /inaseg/requirements.txt
RUN pip3 install --force-reinstall git+https://github.com/grqz/yt-dlp.git@ie/bilibili/pi_fallbk
COPY . /inaseg
RUN python3 /inaseg/biliupinit.py
