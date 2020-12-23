FROM nansencenter/geospaas:latest-slim
LABEL purpose="Environment for REST API for Django-Geo-SpaaS"

# Install Django-rest-framework
RUN apt update && \
    apt install -y git && \
    apt clean && rm -rf /var/lib/apt/lists/* && \
    pip install djangorestframework markdown django-filter 'celery<5.0' 'django-celery-results<2.0'

WORKDIR /src
