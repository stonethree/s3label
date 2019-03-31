#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

# Django:
# python manage.py flush --no-input
# python manage.py migrate

# Flask
# flask run --host=0.0.0.0

exec "$@"