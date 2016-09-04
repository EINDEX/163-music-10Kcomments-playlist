FROM python:3.5.2
MAINTAINER EINDEX snowstarlbk@gmail.com

RUN exit
CMD ls
CMD pip install -r requirements.txt

ENTRYPOINT ["python3", "163music.py"]