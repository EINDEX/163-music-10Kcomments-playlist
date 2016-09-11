FROM python:3.5.2
MAINTAINER EINDEX snowstarlbk@gmail.com

COPY  . /app
WORKDIR /app

ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt -i http://pypi.douban.com/simple --trusted-host pypi.douban.com

CMD ls
EXPOSE 5000
ENTRYPOINT  python3 manager.py runserver --host 0.0.0.0 --port 80