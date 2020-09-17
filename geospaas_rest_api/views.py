"""Views for the GeoSPaaS REST API"""
import django.http
import django_celery_results.models
import geospaas.catalog.models
import geospaas.vocabularies.models
import rest_framework.mixins
from rest_framework.pagination import CursorPagination
from rest_framework.viewsets import GenericViewSet, ReadOnlyModelViewSet

import geospaas_rest_api.filters as filters
import geospaas_rest_api.models as models
import geospaas_rest_api.serializers as serializers


class JobViewSet(rest_framework.mixins.CreateModelMixin,
                 rest_framework.mixins.ListModelMixin,
                 rest_framework.mixins.RetrieveModelMixin,
                 GenericViewSet):
    """API endpoint to manage long running jobs"""
    queryset = models.Job.objects.all().order_by('-id')
    serializer_class = serializers.JobSerializer

    def __init__(self, **kwargs):
        """
        Check for geospaas_processing.tasks availability before allowing to instantiate the viewset.
        Return a 404 error to the client if it is not. This basically disables the tasks endpoint if
        geospaas_processing is not installed.
        """
        if not serializers.tasks:
            raise django.http.Http404()
        super().__init__(**kwargs)


class TaskViewSet(ReadOnlyModelViewSet):
    """API endpoint to manage long running tasks"""
    queryset = django_celery_results.models.TaskResult.objects.all().order_by('-date_created')
    lookup_field = 'task_id'
    serializer_class = serializers.TaskResultSerializer


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
