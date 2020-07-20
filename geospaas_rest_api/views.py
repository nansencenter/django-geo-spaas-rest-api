"""Views for the GeoSPaaS REST API"""
import celery
import celery.result
import django.http
import django_celery_results.models
import geospaas.catalog.models
import geospaas.vocabularies.models
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.viewsets import ReadOnlyModelViewSet

import geospaas_rest_api.filters as filters
import geospaas_rest_api.serializers as serializers


class TaskViewSet(ReadOnlyModelViewSet):
    """API endpoint to manage long running tasks"""
    queryset = django_celery_results.models.TaskResult.objects.all().order_by('-date_created')
    lookup_field = 'task_id'
    serializer_class = serializers.TaskResultSerializer

    def __init__(self, **kwargs):
        """
        Check for geospaas_processing.tasks availability before allowing to instantiate the viewset.
        Return a 404 error to the client if it is not. This basically disables the tasks endpoint if
        geospaas_processing is not installed.
        """
        if not serializers.tasks:
            raise django.http.Http404()
        super().__init__(**kwargs)

    def create(self, request, *args, **kwargs):  # pylint: disable=unused-argument
        """Launches long running tasks using the TaskResultSerializer"""
        serializer = serializers.TaskResultSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        task_url = reverse('taskresult-detail', args=[result.id], request=request)
        return Response(status=202, data={'task_url': task_url})

    def retrieve(self, request, *args, **kwargs):
        """
        Get the task status from the database if it is in progress,
        otherwise get it from the Celery app.
        Drawback: tasks which do not exist are indicated as "PENDING".
        """
        try:
            instance = self.get_object()
        except django.http.Http404:
            result = celery.result.AsyncResult(self.kwargs['task_id'])
            return Response(data={'status': result.status}, status=200)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class GeographicLocationViewSet(ReadOnlyModelViewSet):
    """API endpoint to view GeographicLocations"""
    queryset = geospaas.catalog.models.GeographicLocation.objects.all()
    serializer_class = serializers.GeographicLocationSerializer


class SourceViewSet(ReadOnlyModelViewSet):
    """API endpoint to view Sources"""
    queryset = geospaas.catalog.models.Source.objects.all()
    serializer_class = serializers.SourceSerializer


class InstrumentViewSet(ReadOnlyModelViewSet):
    """API endpoint to view Instruments"""
    queryset = geospaas.vocabularies.models.Instrument.objects.all()
    serializer_class = serializers.InstrumentSerializer


class PlatformViewSet(ReadOnlyModelViewSet):
    """API endpoint to view Platforms"""
    queryset = geospaas.vocabularies.models.Platform.objects.all()
    serializer_class = serializers.PlatformSerializer


class PersonnelViewSet(ReadOnlyModelViewSet):
    """API endpoint to view Personnel objects"""
    queryset = geospaas.catalog.models.Personnel.objects.all()
    serializer_class = serializers.PersonnelSerializer


class RoleViewSet(ReadOnlyModelViewSet):
    """API endpoint to view Roles"""
    queryset = geospaas.catalog.models.Role.objects.all()
    serializer_class = serializers.RoleSerializer


class DatasetViewSet(ReadOnlyModelViewSet):
    """API endpoint to view Datasets"""
    queryset = geospaas.catalog.models.Dataset.objects.all().order_by('time_coverage_start')
    serializer_class = serializers.DatasetSerializer
    filter_backends = [filters.DatasetFilter]


class ParameterViewSet(ReadOnlyModelViewSet):
    """API endpoint to view Parameters"""
    queryset = geospaas.vocabularies.models.Parameter.objects.all()
    serializer_class = serializers.ParameterSerializer


class DatasetURIViewSet(ReadOnlyModelViewSet):
    """API endpoint to view DatasetURIs"""
    queryset = geospaas.catalog.models.DatasetURI.objects.all()
    serializer_class = serializers.DatasetURISerializer
    filter_backends = [filters.DatasetURIFilter]


class DatasetRelationshipViewSet(ReadOnlyModelViewSet):
    """API endpoint to view DatasetRelationships"""
    queryset = geospaas.catalog.models.DatasetRelationship.objects.all()
    serializer_class = serializers.DatasetRelationshipSerializer


class DataCenterViewSet(ReadOnlyModelViewSet):
    """API endpoint to view DataCenters"""
    queryset = geospaas.vocabularies.models.DataCenter.objects.all()
    serializer_class = serializers.DataCenterSerializer
