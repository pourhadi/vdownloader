FROM fnndsc/ubuntu-python3:latest

RUN apt-get update && apt-get --yes install ffmpeg

RUN pip install youtube-dl flask twisted redis

RUN mkdir /app

RUN mkdir /videos

VOLUME /app

VOLUME /videos

EXPOSE 5000/tcp

ENTRYPOINT ["python", "/app/app.py"]

#ENTRYPOINT ["/bin/bash"]