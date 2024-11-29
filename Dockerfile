FROM tensorflow/tensorflow:2.18.0
RUN apt update
RUN apt -y install ffmpeg aria2 wget nano git
WORKDIR /inaseg
COPY ./requirements.txt /inaseg/requirements.txt
RUN git clone https://github.com/ina-foss/inaSpeechSegmenter.git
RUN cd inaSpeechSegmenter; pip install .
RUN pip3 install -r /inaseg/requirements.txt
RUN pip3 install --force-reinstall git+https://github.com/grqz/yt-dlp.git@ie/bilibili/pi_fallbk
COPY . /inaseg
RUN python3 /inaseg/biliupinit.py
