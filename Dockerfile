ARG BASE_IMAGE=nansencenter/geospaas:latest
FROM ${BASE_IMAGE}
LABEL purpose="Environment for REST API for Django-Geo-SpaaS"

ARG GEOSPAAS_PROCESSING_VERSION
ARG GEOSPAAS_HARVESTING_VERSION
ARG METANORM_VERSION

# Install Django-rest-framework
RUN apt update && \
    apt install -y git nco && \
    apt clean && rm -rf /var/lib/apt/lists/* && \
    pip install --upgrade --no-cache-dir \
    'celery==5.2.*' \
    'django-celery-results==2.2.*' \
    'django==3.*' \
    django-filter \
    djangorestframework \
    djangorestframework-filters==1.0.0dev2 \
    'importlib-metadata==4.*' \
    markdown \
    "https://github.com/nansencenter/django-geo-spaas-processing/releases/download/${GEOSPAAS_PROCESSING_VERSION}/geospaas_processing-${GEOSPAAS_PROCESSING_VERSION}-py3-none-any.whl" \
    "https://github.com/nansencenter/django-geo-spaas-harvesting/releases/download/${GEOSPAAS_HARVESTING_VERSION}/geospaas_harvesting-${GEOSPAAS_HARVESTING_VERSION}-py3-none-any.whl" \
    "https://github.com/nansencenter/metanorm/releases/download/${METANORM_VERSION}/metanorm-${METANORM_VERSION}-py3-none-any.whl"

WORKDIR /src
