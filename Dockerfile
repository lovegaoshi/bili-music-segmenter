FROM tensorflow/tensorflow:2.18.0
RUN apt-get update --allow-insecure-repositories
RUN apt-get -y --allow-unauthenticated install ffmpeg aria2 wget nano git
WORKDIR /inaseg
RUN git clone https://github.com/lovegaoshi/inaSpeechSegmenter.git
RUN cd inaSpeechSegmenter; pip install .
RUN pip3 install pandas==2.0.0
COPY ./requirements.txt /inaseg/requirements.txt
RUN pip3 install -r /inaseg/requirements.txt
# fix numpy to be 1.23.0; inaspeechsegmenter uses a deprecated feature that breaks on numpy > 2
RUN pip3 install numpy==1.23.0
RUN pip3 install --force-reinstall git+https://github.com/grqz/yt-dlp.git@ie/bilibili/pi_fallbk
RUN wget https://getsamplefiles.com/download/mp3/sample-1.mp3 -P /home
COPY . /inaseg
RUN python3 /inaseg/biliupinit.py
# Testing
RUN python3 /inaseg/inaseg.py --media /home/sample-1.mp3