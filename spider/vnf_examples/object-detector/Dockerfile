FROM python:3.8-slim
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y  wget
RUN mkdir /app

WORKDIR /app
COPY requirements.txt /app
COPY config_vnf.json /app
COPY vnf_interface.py /app
COPY download_weights.sh /app

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN ./download_weights.sh
COPY . /app

EXPOSE 5000
CMD [ "python", "object_detector.py"]

