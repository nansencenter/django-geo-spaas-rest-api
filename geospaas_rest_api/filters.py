"""
Custom filters for the REST API
"""
import re
import datetime

import dateutil.parser
from django.contrib.gis.geos import GEOSGeometry
from django.db.models import Value
from django.db.models.functions import Concat
from django.template import loader

from rest_framework.exceptions import ValidationError
from rest_framework.filters import BaseFilterBackend


class DatasetFilter(BaseFilterBackend):
    """
    Enables filtering of Datasets based on date, location and source
    """

    DATE_PARAM = 'date'
    LOCATION_PARAM = 'zone'
    SOURCE_PARAM = 'source'

    BROWSABLE_TEMPLATE = 'geospaas_rest_api/search.html'

    RANGE_MATCHER = re.compile(r'^\(([^()]+),([^()]+)\)$')

    def filter_queryset(self, request, queryset, view):
        """
        Filter the queryset based on request arguments
        """
        filtered_queryset = queryset
        if self.DATE_PARAM in request.query_params and request.query_params[self.DATE_PARAM]:
            range_match = self.RANGE_MATCHER.match(request.query_params[self.DATE_PARAM])
            try:
                if range_match:
                    date_range = [dateutil.parser.parse(date) for date in range_match.groups()]
                else:
                    date_range = [dateutil.parser.parse(request.query_params[self.DATE_PARAM]),] * 2
            except dateutil.parser.ParserError:
                raise ValidationError("Wrong date format", code=400)

            # If the timezone is not specified, UTC is assumed
            for i, date in enumerate(date_range):
                if not date.tzinfo:
                    date_range[i] = date.replace(tzinfo=datetime.timezone.utc)

            if date_range[0] > date_range[1]:
                raise ValidationError(
                    detail="The first date in the range should be inferior to the second one",
                    code=400)

            filtered_queryset = filtered_queryset.filter(
                time_coverage_start__lte=date_range[1], time_coverage_end__gte=date_range[0])
        if self.SOURCE_PARAM in request.query_params and request.query_params[self.SOURCE_PARAM]:
            source_keyword = request.query_params[self.SOURCE_PARAM]
            filtered_queryset = filtered_queryset.annotate(source_search_name=Concat(
                'source__platform__short_name', Value('_'), 'source__instrument__short_name'
            )).filter(source_search_name__icontains=source_keyword)
        if self.LOCATION_PARAM in request.query_params and \
                request.query_params[self.LOCATION_PARAM]:
            zone = GEOSGeometry(request.query_params[self.LOCATION_PARAM])
            filtered_queryset = filtered_queryset.filter(
                geographic_location__geometry__intersects=zone
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
