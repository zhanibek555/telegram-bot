FROM python:3

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY . /usr/src/app
RUN pip --proxy "http://registry.sergek.kz:3128/" install --upgrade pip
RUN pip --proxy "http://registry.sergek.kz:3128/" install --trusted-host pypi.python.org -r requirements

CMD ["python3", "script.py"]


