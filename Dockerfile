FROM tensorflow/tensorflow:latest
COPY . /inaseg
WORKDIR /inaseg
RUN pip install -r /inaseg/requirements.txt
RUN apt update
RUN apt -y install ffmpeg aria2 wget
RUN python /inaseg/initialize.py 