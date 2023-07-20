# Використовуємо базовий образ Python 3.10
FROM python:3.10

LABEL authors="dev"

ENV DockerHome=/app
# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir -p $DockerHome

WORKDIR $DockerHome

# Встановлюємо залежності
RUN apt-get update \
    && apt-get install -y \
        postgresql \
        wkhtmltopdf \
    && rm -rf /var/lib/apt/lists/*

# Встановлюємо залежності Python
COPY requirements.txt /$DockerHome/requirements.txt
RUN pip install --no-cache-dir -r /$DockerHome/requirements.txt

# Копіюємо код додатку у контейнер
COPY . $DockerHome

# Запускаємо entrypoint.sh при старті контейнера
CMD ["./entrypoint.sh"]