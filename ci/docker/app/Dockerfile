FROM python:3-alpine

# See [https://testdriven.io/blog/dockerizing-django-with-postgres-gunicorn-and-nginx/]

# Environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install psycopg2 (Alpine requires some hand-holding)
RUN apk update \
    && apk add --virtual build-deps gcc python3-dev musl-dev \
    && apk add postgresql-dev \
    && pip install psycopg2 \
    && apk del build-deps

# Install python dependencies (Execute this first to take advantage of Docker layering)
COPY ./requirements.txt /
RUN pip install -r /requirements.txt

# Application directory
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# Copy entrypoint.sh to the container
COPY ./docker-entrypoint.sh /usr/src/app/

# Copy project to the container
COPY . /usr/src/app/

# Expose the app on port 5000
EXPOSE 5000

# Run docker-entrypoint.sh
ENTRYPOINT ["/usr/src/app/docker-entrypoint.sh"]

# Run the Flask server
# ENTRYPOINT [ "flask" ]
# CMD [ "run", "--host=0.0.0.0"]

