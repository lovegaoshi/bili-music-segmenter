FROM tensorflow/tensorflow:2.13.0
RUN apt update
RUN apt -y install ffmpeg aria2 wget nano
WORKDIR /inaseg
COPY ./requirements.txt /inaseg/requirements.txt
RUN pip install -r /inaseg/requirements.txt
RUN pip install --force-reinstall git+https://github.com/grqz/yt-dlp.git@ie/bilibili/pi_fallbk
COPY . /inaseg
RUN python /inaseg/biliupinit.py
