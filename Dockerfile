FROM ubuntu:latest

RUN apt-get update
RUN apt-get install -y build-essential python3.6 python3.6-dev python3-pip python3.6-venv git
RUN python3.6 -m pip install pip --upgrade
RUN python3.6 -m pip install wheel

RUN python3.6 -m pip install joblib nltk numpy pandas pydub scikit-learn SpeechRecognition six python-dateutil

RUN apt-get install -y ffmpeg

WORKDIR /App
ADD ./App/nltk_load_new.py /App

RUN python3.6 nltk_load_new.py

RUN mkdir -p /App/out
RUN mkdir -p /App/audio

ADD ./App /App
RUN python3.6 generate_model.py

ENTRYPOINT ["python3.6", "./predict.py"]