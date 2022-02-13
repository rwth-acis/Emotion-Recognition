FROM python:3.7.11 
ADD app.py /
COPY . /app
WORKDIR /app
COPY ./static/ /static
RUN apt-get update
RUN apt-get install libasound-dev libportaudio2 libportaudiocpp0 portaudio19-dev -y
RUN pip3 install pyaudio
RUN pip3 install Flask
RUN pip3 install flask-swagger-ui
RUN pip3 install SpeechRecognition
RUN pip3 install pydub
RUN pip3 install librosa==0.6.3
RUN pip3 install numpy
RUN pip3 install pandas
RUN pip3 install soundfile==0.9.0
RUN pip3 install wave
RUN pip3 install sklearn
RUN pip3 install tqdm==4.28.1
RUN pip3 install matplotlib==2.2.3
RUN pip3 install pyaudio==0.2.11
RUN pip3 install tensorflow==2.5.2
RUN pip3 install numba==0.48
RUN pip3 install pymongo
RUN apt-get -y update
RUN apt-get install -y ffmpeg
RUN pip3 install ffmpeg-python

EXPOSE 5002
CMD ["python3", "./app.py"]