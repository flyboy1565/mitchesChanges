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

ENV PORT=8000

# install psycopg2 dependencies
# RUN apt-get -o Acquire::Check-Valid-Until=false -o Acquire::Check-Date=false update
# RUN apt-get update 
# RUN apt-get upgrade -y 
RUN apt-get install -y --no-install-recommends tzdata 
RUN apt-get install -y --no-install-recommends python3-pip 
RUN apt-get install -y --no-install-recommends postgresql 
RUN apt-get install -y --no-install-recommends libpq-dev 
RUN apt-get install -y --no-install-recommends postgresql-client 
RUN apt-get install -y --no-install-recommends postgresql-client-common 
RUN apt-get install -y --no-install-recommends git 
# RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/*z

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt /app/requirements.txt
COPY ./entrypoint.sh .
RUN pip install -r /app/requirements.txt
RUN pip install psycopg2-binary

ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
# CMD gunicorn hsweb.wsgi:application --bind 0.0.0.0:$PORT 
CMD ["python", "manage.py", "runserver", "0.0.0.0", "8000"]