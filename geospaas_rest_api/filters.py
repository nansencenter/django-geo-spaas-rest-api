"""
Custom filters for the REST API
"""
from dateutil.parser import parse as dateutil_parse
from django.contrib.gis.geos import GEOSGeometry
from django.db.models import Q
from django.template import loader

from rest_framework.filters import BaseFilterBackend


class DatasetFilter(BaseFilterBackend):
    """
    Enables filtering of Datasets based on date, location and source
    """

    DATE_PARAM = 'date'
    LOCATION_PARAM = 'zone'
    SOURCE_PARAM = 'source'

    BROWSABLE_TEMPLATE = 'geospaas_rest_api/search.html'

    def filter_queryset(self, request, queryset, view):
        """
        Filter the queryset based on request arguments
        """
        filtered_queryset = queryset
        if self.DATE_PARAM in request.query_params and request.query_params[self.DATE_PARAM]:
            filtered_queryset = filtered_queryset.filter(
                time_coverage_start__lte=dateutil_parse(request.query_params[self.DATE_PARAM]),
                time_coverage_end__gte=dateutil_parse(request.query_params[self.DATE_PARAM])
            )
        if self.LOCATION_PARAM in request.query_params and \
           request.query_params[self.LOCATION_PARAM]:
            zone = GEOSGeometry(request.query_params[self.LOCATION_PARAM])
            filtered_queryset = filtered_queryset.filter(
                geographic_location__geometry__intersects=zone
            )
        if self.SOURCE_PARAM in request.query_params and request.query_params[self.SOURCE_PARAM]:
            filtered_queryset = filtered_queryset.filter(
                Q(source__platform__short_name__icontains=request.query_params[self.SOURCE_PARAM]) |
                Q(source__instrument__short_name__icontains=request.query_params[self.SOURCE_PARAM])
            )
        return filtered_queryset

    def to_html(self, request, queryset, view):  # pylint: disable=unused-argument
        """
        Enables filtering in the browsable API
        """
        if self.DATE_PARAM in request.query_params:
            date_term = request.query_params[self.DATE_PARAM]
        else:
            date_term = ''

        if self.LOCATION_PARAM in request.query_params:
            location_term = request.query_params[self.LOCATION_PARAM]
        else:
            location_term = ''

        if self.SOURCE_PARAM in request.query_params:
            source_term = request.query_params[self.SOURCE_PARAM]
        else:
            source_term = ''

        context = {
            'params': [self.DATE_PARAM, self.LOCATION_PARAM, self.SOURCE_PARAM],
            'terms': [date_term, location_term, source_term]
        }

        template = loader.get_template(self.BROWSABLE_TEMPLATE)
        return template.render(context)


class DatasetURIFilter(BaseFilterBackend):
    """
    Enables filtering of DatasetURI based on Dataset ID
    """

    DATASET_PARAM = 'dataset'

    def filter_queryset(self, request, queryset, view):
        filtered_queryset = queryset
        if self.DATASET_PARAM in request.query_params and request.query_params[self.DATASET_PARAM]:
            filtered_queryset = filtered_queryset.filter(
                dataset__id=request.query_params[self.DATASET_PARAM]
            )
        return filtered_queryset
