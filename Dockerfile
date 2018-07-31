FROM ubuntu:16.04
RUN apt-get update

RUN apt-get -y install python-dev python-pip python3-dev python3-pip
RUN apt-get -y install uwsgi-plugin-python3
RUN apt-get -y install curl sudo vim openssh-server zsh
RUN apt-get clean

RUN python3 -m pip install --upgrade pip setuptools
RUN python3 -m pip install uwsgi

ADD ./app /app
WORKDIR /app
RUN python3 -m pip install -r requirements.txt

EXPOSE 5000

# CMD ["/bin/bash"]
CMD ["uwsgi", "--ini=wsgi.ini"]
