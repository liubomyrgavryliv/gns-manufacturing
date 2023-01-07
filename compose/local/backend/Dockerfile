FROM arm64v8/python:3.10

ENV PYTHONUNBUFFERED 1

RUN apt-get update -y && apt-get install -y \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

RUN python -m pip install --upgrade pip

WORKDIR /app
COPY src/requirements/base.txt src/requirements/base.txt
COPY src/requirements/development.txt src/requirements/development.txt
RUN python -m pip install -r src/requirements/development.txt

WORKDIR /app/src

COPY ./compose/prod/backend/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint

COPY ./compose/local/backend/start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start

# Copy project code files
COPY . /app

ENTRYPOINT ["/entrypoint"]
