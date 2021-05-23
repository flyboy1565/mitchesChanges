FROM python:3.8
RUN apt-get update && apt-get upgrade -y
RUN mkdir /app
WORKDIR /app
ADD . /app/
COPY . /app/

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DEBIAN_FRONTEND=noninteractive 

# ENV PORT=8000


# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt


# ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
# CMD gunicorn hsweb.wsgi:application --bind 0.0.0.0:$PORT 
CMD ["python", "chat_bot.py"]