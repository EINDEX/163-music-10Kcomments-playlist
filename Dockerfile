FROM python:3.5.2
MAINTAINER EINDEX snowstarlbk@gmail.com

COPY  . /app
WORKDIR /app

ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt -i http://pypi.douban.com/simple --trusted-host pypi.douban.com

CMD ["python3","163music.py"]