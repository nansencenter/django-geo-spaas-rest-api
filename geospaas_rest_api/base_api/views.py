"""Views for the base geospaas API"""
import geospaas.catalog.models
import geospaas.vocabularies.models
from rest_framework.viewsets import ReadOnlyModelViewSet

import geospaas_rest_api.base_api.filters as filters
import geospaas_rest_api.base_api.serializers as serializers


class KeywordViewSet(ReadOnlyModelViewSet):
    """API endpoint to view Keywords"""
    queryset = geospaas.vocabularies.models.Keyword.objects.all()
    serializer_class = serializers.KeywordSerializer
    filterset_class = filters.KeywordFilter


class ParameterViewSet(ReadOnlyModelViewSet):
    """API endpoint to view Parameters"""
    queryset = geospaas.vocabularies.models.Parameter.objects.all()
    serializer_class = serializers.ParameterSerializer
    filterset_class = filters.ParameterFilter


class TagViewSet(ReadOnlyModelViewSet):
    """API endpoint to view Tag"""
    queryset = geospaas.catalog.models.Tag.objects.all()
    serializer_class = serializers.TagSerializer
    filterset_class = filters.TagFilter


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
