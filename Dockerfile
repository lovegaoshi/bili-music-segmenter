FROM tensorflow/tensorflow:latest
COPY . /inaseg
RUN pip install -r /inaseg/requirements.txt
RUN apt update
RUN apt -y install ffmpeg aria2
RUN python /inaseg/initialize.py