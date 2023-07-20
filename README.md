# gen_checks

API microservice for generating checks by orders

## Description

Generation checks is API microservice for generating checks by orders.

A delivery restaurant chain has many locations where orders are prepared for customers. 
Every customer wants a receipt along with their order, containing detailed information about the order. 
The kitchen staff also wants the receipt so that during the process of cooking and packing the order, 
they don't forget to put everything they need. Generation checks helps with this.

[Celery](https://docs.celeryq.dev/en/stable/) asynchronous queue 
(based on [Redis](https://redis.io/) message broker) is used to perform check rendering tasks. 
Conversion to PDF is performed via [wkhtmltopdf](https://wkhtmltopdf.org/).

### Work scheme
[Task description](https://docs.google.com/document/d/1NWZo6nQdofRzL-3QASDmTF75M0PJOy-YJAalQZr9dgE/edit?usp=sharing)

## Usage

You can deploy the project via Docker.

[Docker website](https://www.docker.com/).

[install Docker Desktop](https://www.docker.com/products/docker-desktop/).

#### Environment
`.env`
```
# DB
POSTGRES_DB=gen_checks
POSTGRES_USER=test
POSTGRES_PASSWORD=test
POSTGRES_HOST=db
POSTGRES_PORT=5432

# app
DEBUG=True
SECRET_KEY={Add_your_secret_key}
ALLOWED_HOSTS=127.0.0.1
DATABASE_URL=postgres://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}

# celery
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=${CELERY_BROKER_URL}

# wkhtmltopdf
WKHTMLTOPDF_URL=http://wkhtmltopdf:80
```

#### Run
```bash
>> docker-compose up -d --build

...
...
...
gen_checks_app_1           ... done
gen_checks_celery_1        ... done                                              
gen_checks_db_1            ... done
gen_checks_flower_1        ... done
gen_checks_redis_1         ... done
gen_checks_wkhtmltopdf_1   ... done
```

Open - http://127.0.0.1:8000

API documentation - http://127.0.0.1:8000/swagger-ui/ or http://127.0.0.1:8000/redoc/

Flower monitoring - http://127.0.0.1:5555/
                           