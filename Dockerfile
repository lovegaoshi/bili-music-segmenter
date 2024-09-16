FROM tensorflow/tensorflow:2.13.0
RUN apt update
RUN apt -y install ffmpeg aria2 wget nano
WORKDIR /inaseg
COPY ./requirements.txt /inaseg/requirements.txt
RUN pip install -r /inaseg/requirements.txt
COPY . /inaseg
RUN python /inaseg/biliupinit.py
