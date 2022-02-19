FROM python:3.7.11 
ADD app.py /
COPY . /app
WORKDIR /app
COPY ./static/ /static
RUN apt-get -y update
RUN apt-get install libasound-dev libportaudio2 libportaudiocpp0 portaudio19-dev -y
RUN pip install -r requirements.txt
RUN apt-get install -y ffmpeg
RUN pip3 install ffmpeg-python

EXPOSE 5002
CMD ["python3", "./app.py"]