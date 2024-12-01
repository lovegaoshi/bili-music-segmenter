FROM python:3.11
WORKDIR /app
COPY . /app
RUN pip install requests pyyaml
CMD python bilitagfixer.py