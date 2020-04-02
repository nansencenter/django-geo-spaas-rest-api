FROM geospaas:latest
LABEL purpose="Environment for REST API for Django-Geo-SpaaS"
ENV PYTHONUNBUFFERED=1

# Install Django
RUN pip install \
    djangorestframework \
    markdown \
    django-filter 

WORKDIR /src
