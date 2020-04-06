"""
Views for the GeoSPaaS REST API
"""
from rest_framework.viewsets import ReadOnlyModelViewSet
from geospaas_rest_api.filters import DatasetFilter, DatasetURIFilter
from geospaas_rest_api.serializers import (GeographicLocationSerializer, SourceSerializer,
                                           PersonnelSerializer, RoleSerializer, DatasetSerializer,
                                           DatasetParameterSerializer, DatasetURISerializer,
                                           DatasetRelationshipSerializer, InstrumentSerializer,
                                           PlatformSerializer, DataCenterSerializer)
from geospaas.catalog.models import (GeographicLocation, Source, Personnel, Role, Dataset,
                                     DatasetParameter, DatasetURI, DatasetRelationship)
from geospaas.vocabularies.models import DataCenter, Instrument, Platform


class GeographicLocationViewSet(ReadOnlyModelViewSet):
    """
    API endpoint to view GeographicLocations
    """
    queryset = GeographicLocation.objects.all()
    serializer_class = GeographicLocationSerializer


class SourceViewSet(ReadOnlyModelViewSet):
    """
    API endpoint to view Sources
    """
    queryset = Source.objects.all()
    serializer_class = SourceSerializer


class InstrumentViewSet(ReadOnlyModelViewSet):
    """
    API endpoint to view Instruments
    """
    queryset = Instrument.objects.all()
    serializer_class = InstrumentSerializer


class PlatformViewSet(ReadOnlyModelViewSet):
    """
    API endpoint to view Platforms
    """
    queryset = Platform.objects.all()
    serializer_class = PlatformSerializer


class PersonnelViewSet(ReadOnlyModelViewSet):
    """
    API endpoint to view Personnel objects
    """
    queryset = Personnel.objects.all()
    serializer_class = PersonnelSerializer


class RoleViewSet(ReadOnlyModelViewSet):
    """
    API endpoint to view Roles
    """
    queryset = Role.objects.all()
    serializer_class = RoleSerializer


class DatasetViewSet(ReadOnlyModelViewSet):
    """
    API endpoint to view Datasets
    """
    queryset = Dataset.objects.all().order_by('time_coverage_start')
    serializer_class = DatasetSerializer
    filter_backends = [DatasetFilter]


class DatasetParameterViewSet(ReadOnlyModelViewSet):
    """
    API endpoint to view DatasetParameters
    """
    queryset = DatasetParameter.objects.all()
    serializer_class = DatasetParameterSerializer


class DatasetURIViewSet(ReadOnlyModelViewSet):
    """
    API endpoint to view DatasetURIs
    """
    queryset = DatasetURI.objects.all()
    serializer_class = DatasetURISerializer
    filter_backends = [DatasetURIFilter]


class DatasetRelationshipViewSet(ReadOnlyModelViewSet):
    """
    API endpoint to view DatasetRelationships
    """
    queryset = DatasetRelationship.objects.all()
    serializer_class = DatasetRelationshipSerializer


class DataCenterViewSet(ReadOnlyModelViewSet):
    """
    API endpoint to view DataCenters
    """
    queryset = DataCenter.objects.all()
    serializer_class = DataCenterSerializer
