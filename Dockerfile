FROM fnndsc/ubuntu-python3:latest

RUN apt-get update && apt-get --yes install ffmpeg

RUN pip install youtube-dl flask twisted redis

RUN mkdir /app

RUN mkdir /videos

#COPY ./app/app.py /app
#COPY app/downloader.py /videos

VOLUME /app
VOLUME /videos

EXPOSE 80/tcp

ENTRYPOINT ["python", "/app/app.py"]

#ENTRYPOINT ["/bin/bash"]