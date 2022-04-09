FROM python:3.7

ENV PYTHONUNBUFFERED 1

RUN apt-get update -y && apt-get install -y \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

RUN python -m pip install --upgrade pip

WORKDIR /app
COPY src/requirements/base.txt src/requirements/base.txt
COPY src/requirements/development.txt src/requirements/development.txt
RUN python -m pip install -r src/requirements/development.txt

EXPOSE 8000
WORKDIR /app/src
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]