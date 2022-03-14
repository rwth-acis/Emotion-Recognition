FROM python:3.7.11 
ADD app.py /
COPY . /app
WORKDIR /app
COPY ./static/ /static
RUN apt-get -y update &&\
    apt-get install swig libpulse-dev libasound-dev libportaudio2 libportaudiocpp0 portaudio19-dev ffmpeg -y &&\
    pip install -r requirements.txt &&\
    pip3 install ffmpeg-python


EXPOSE 5002
CMD ["python3", "./app.py"]

# I still have to check wether i will have to install pocketsphinx with pipwin, but given it is a linux system this might not be necesary