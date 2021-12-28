FROM python:3.8-slim
ENV PYTHONUNBUFFERED 1
RUN apt-get update && apt-get install -y python3-opencv
RUN mkdir /app
WORKDIR /app
COPY requirements.txt /app
COPY config_vnf.json /app
COPY vnf_interface.py /app
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
COPY . /app
EXPOSE 5000
CMD [ "python", "compress_image.py"]
