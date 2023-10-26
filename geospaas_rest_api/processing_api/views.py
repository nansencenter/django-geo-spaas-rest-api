"""Views for the processing API"""
import django_celery_results.models
import rest_framework.mixins
import geospaas_processing.models
from rest_framework.viewsets import GenericViewSet, ReadOnlyModelViewSet

import geospaas_rest_api.models as models
import geospaas_rest_api.pagination as pagination
import geospaas_rest_api.processing_api.filters as filters
import geospaas_rest_api.processing_api.serializers as serializers


class JobViewSet(rest_framework.mixins.CreateModelMixin,
                 rest_framework.mixins.ListModelMixin,
                 rest_framework.mixins.RetrieveModelMixin,
                 GenericViewSet):
    """API endpoint to manage long running jobs"""
    queryset = models.Job.objects.all()
    serializer_class = serializers.JobSerializer
    pagination_class = pagination.IdOrderedCursorPagination


class TaskViewSet(ReadOnlyModelViewSet):
    """API endpoint to manage long running tasks"""
    queryset = django_celery_results.models.TaskResult.objects.all()
    lookup_field = 'task_id'
    serializer_class = serializers.TaskResultSerializer
    pagination_class = pagination.DateOrderedCursorPagination


class ProcessingResultViewSet(ReadOnlyModelViewSet):
    """API endpoint to view ProcessingResults"""
    queryset = geospaas_processing.models.ProcessingResult.objects.all().order_by('created')
    serializer_class = serializers.ProcessingResultSerializer
    filterset_class = filters.ProcessingResultFilter
