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


class DateOrderedCursorPagination(CursorPagination):
    """Pagination class ordering by decreasing date_created"""
    ordering = '-date_created'
    page_size = 100


class IdOrderedCursorPagination(CursorPagination):
    """Pagination class ordering by decreasing date_created"""
    ordering = '-id'
    page_size = 100


class JobViewSet(rest_framework.mixins.CreateModelMixin,
                 rest_framework.mixins.ListModelMixin,
                 rest_framework.mixins.RetrieveModelMixin,
                 GenericViewSet):
    """API endpoint to manage long running jobs"""
    queryset = models.Job.objects.all()
    serializer_class = serializers.JobSerializer
    pagination_class = IdOrderedCursorPagination


class TaskViewSet(ReadOnlyModelViewSet):
    """API endpoint to manage long running tasks"""
    queryset = django_celery_results.models.TaskResult.objects.all()
    lookup_field = 'task_id'
    serializer_class = serializers.TaskResultSerializer
    pagination_class = DateOrderedCursorPagination


class GeographicLocationViewSet(ReadOnlyModelViewSet):
    """API endpoint to view GeographicLocations"""
    queryset = geospaas.catalog.models.GeographicLocation.objects.all()
    serializer_class = serializers.GeographicLocationSerializer
    filterset_class = filters.GeographicLocationFilter


class SourceViewSet(ReadOnlyModelViewSet):
    """API endpoint to view Sources"""
    queryset = geospaas.catalog.models.Source.objects.all()
    serializer_class = serializers.SourceSerializer
    filterset_class = filters.SourceFilter


class InstrumentViewSet(ReadOnlyModelViewSet):
    """API endpoint to view Instruments"""
    queryset = geospaas.vocabularies.models.Instrument.objects.all()
    serializer_class = serializers.InstrumentSerializer
    filterset_class = filters.InstrumentFilter


class PlatformViewSet(ReadOnlyModelViewSet):
    """API endpoint to view Platforms"""
    queryset = geospaas.vocabularies.models.Platform.objects.all()
    serializer_class = serializers.PlatformSerializer
    filterset_class = filters.PlatformFilter


class PersonnelViewSet(ReadOnlyModelViewSet):
    """API endpoint to view Personnel objects"""
    queryset = geospaas.catalog.models.Personnel.objects.all()
    serializer_class = serializers.PersonnelSerializer
    filterset_class = filters.PersonnelFilter


class RoleViewSet(ReadOnlyModelViewSet):
    """API endpoint to view Roles"""
    queryset = geospaas.catalog.models.Role.objects.all()
    serializer_class = serializers.RoleSerializer
    filterset_class = filters.RoleFilter


class DatasetViewSet(ReadOnlyModelViewSet):
    """API endpoint to view Datasets"""
    queryset = geospaas.catalog.models.Dataset.objects.all().order_by('time_coverage_start')
    serializer_class = serializers.DatasetSerializer
    filterset_class = filters.DatasetFilter


class ParameterViewSet(ReadOnlyModelViewSet):
    """API endpoint to view Parameters"""
    queryset = geospaas.vocabularies.models.Parameter.objects.all()
    serializer_class = serializers.ParameterSerializer
    filterset_class = filters.ParameterFilter


class DatasetURIViewSet(ReadOnlyModelViewSet):
    """API endpoint to view DatasetURIs"""
    queryset = geospaas.catalog.models.DatasetURI.objects.all()
    serializer_class = serializers.DatasetURISerializer
    filterset_class = filters.DatasetURIFilter


class DatasetRelationshipViewSet(ReadOnlyModelViewSet):
    """API endpoint to view DatasetRelationships"""
    queryset = geospaas.catalog.models.DatasetRelationship.objects.all()
    serializer_class = serializers.DatasetRelationshipSerializer
    filterset_class = filters.DatasetRelationshipFilter


class DataCenterViewSet(ReadOnlyModelViewSet):
    """API endpoint to view DataCenters"""
    queryset = geospaas.vocabularies.models.DataCenter.objects.all()
    serializer_class = serializers.DataCenterSerializer
    filterset_class = filters.DataCenterFilter


class ISOTopicCategoryViewSet(ReadOnlyModelViewSet):
    """API endpoint to view ISOTopicCategories"""
    queryset = geospaas.vocabularies.models.ISOTopicCategory.objects.all()
    serializer_class = serializers.ISOTopicCategorySerializer
    filterset_class = filters.ISOTopicCategoryFilter


class ScienceKeywordViewSet(ReadOnlyModelViewSet):
    """API endpoint to view ScienceKeywords"""
    queryset = geospaas.vocabularies.models.ScienceKeyword.objects.all()
    serializer_class = serializers.ScienceKeywordSerializer
    filterset_class = filters.ScienceKeywordFilter


class LocationViewSet(ReadOnlyModelViewSet):
    """API endpoint to view Locations"""
    queryset = geospaas.vocabularies.models.Location.objects.all()
    serializer_class = serializers.LocationSerializer
    filterset_class = filters.LocationFilter
