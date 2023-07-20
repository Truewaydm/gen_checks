FROM python:3.10

LABEL authors="dev"

ENV DockerHome=/app
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir -p $DockerHome

WORKDIR $DockerHome

RUN apt-get update \
    && apt-get install -y \
        postgresql \
        wkhtmltopdf \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /$DockerHome/requirements.txt
RUN pip install --no-cache-dir -r /$DockerHome/requirements.txt

COPY . $DockerHome

CMD ["./entrypoint.sh"]