FROM nansencenter/geospaas:latest-slim
LABEL purpose="Environment for REST API for Django-Geo-SpaaS"

# Install Django-rest-framework
RUN pip install djangorestframework markdown django-filter

WORKDIR /src
