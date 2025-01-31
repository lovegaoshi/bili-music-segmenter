FROM tensorflow/tensorflow:2.18.0
RUN apt-get update
RUN apt-get -y install ffmpeg aria2 wget nano git
WORKDIR /inaseg
RUN git clone https://github.com/lovegaoshi/inaSpeechSegmenter.git
RUN cd inaSpeechSegmenter; pip install .
RUN pip3 install pandas==2.0.0
COPY ./requirements.txt /inaseg/requirements.txt
RUN pip3 install -r /inaseg/requirements.txt
# fix numpy to be 1.26; inaspeechsegmenter uses a deprecated feature that breaks on numpy > 2
RUN pip3 install numpy==1.26.3
RUN wget https://getsamplefiles.com/download/mp3/sample-1.mp3 -P /home
COPY . /inaseg
RUN python3 /inaseg/biliupinit.py
# Testing
RUN python3 /inaseg/inaseg.py --media /home/sample-1.mp3