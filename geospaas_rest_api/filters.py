"""
Custom filters for the REST API
"""
import datetime
import re

import dateutil.parser
import rest_framework_filters
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.db.models import GeometryField
from django.db.models import Value
from django.db.models.functions import Concat
from django.template import loader
from django_filters.rest_framework.filters import CharFilter
from rest_framework.exceptions import ValidationError
from rest_framework.filters import BaseFilterBackend

import geospaas.catalog.models
import geospaas.vocabularies.models


class ScienceKeywordFilter(rest_framework_filters.FilterSet):
    """Filter for ScienceKeyword"""
    class Meta:
        model = geospaas.vocabularies.models.ScienceKeyword
        fields = {
            'category': '__all__',
            'topic': '__all__',
            'term': '__all__',
            'variable_level_1': '__all__',
            'variable_level_2': '__all__',
            'variable_level_3': '__all__',
            'detailed_variable': '__all__',
        }


class ParameterFilter(rest_framework_filters.FilterSet):
    """Filter for Parameters"""
    gcmd_science_keyword = rest_framework_filters.RelatedFilter(
        ScienceKeywordFilter,
        field_name='gcmd_science_keyword',
        queryset=geospaas.vocabularies.models.ScienceKeyword.objects.all()
    )
    class Meta:
        model = geospaas.vocabularies.models.Parameter
        fields = {
            'standard_name': '__all__',
            'short_name': '__all__',
            'units': '__all__',
        }


class InstrumentFilter(rest_framework_filters.FilterSet):
    """Filter for Instruments"""
    class Meta:
        model = geospaas.vocabularies.models.Instrument
        fields = {
            'category': '__all__',
            'instrument_class': '__all__',
            'type': '__all__',
            'subtype': '__all__',
            'short_name': '__all__',
            'long_name': '__all__',
        }


class PlatformFilter(rest_framework_filters.FilterSet):
    """Filter for Platforms"""
    class Meta:
        model = geospaas.vocabularies.models.Platform
        fields = {
            'category': '__all__',
            'series_entity': '__all__',
            'short_name': '__all__',
            'long_name': '__all__',
        }


class DataCenterFilter(rest_framework_filters.FilterSet):
    """Filter for DataCenters"""
    class Meta:
        model = geospaas.vocabularies.models.DataCenter
        fields = {
            'bucket_level0': '__all__',
            'bucket_level1': '__all__',
            'bucket_level2': '__all__',
            'bucket_level3': '__all__',
            'short_name': '__all__',
            'long_name': '__all__',
            'data_center_url': '__all__',
        }


class ISOTopicCategoryFilter(rest_framework_filters.FilterSet):
    """Filter for ISOTopicCategories"""
    class Meta:
        model = geospaas.vocabularies.models.ISOTopicCategory
        fields = {'name': '__all__'}


class LocationFilter(rest_framework_filters.FilterSet):
    """Filter for Locations"""
    class Meta:
        model = geospaas.vocabularies.models.Location
        fields = {
            'category': '__all__',
            'type': '__all__',
            'subregion1': '__all__',
            'subregion2': '__all__',
            'subregion3': '__all__',
        }


class GeographicLocationFilter(rest_framework_filters.FilterSet):
    """Filter for GeographicLocations"""

    class Meta:
        model = geospaas.catalog.models.GeographicLocation
        fields = {'geometry': '__all__'}
        # We have to define the filter used for GeometryFields
        # because it's not supported natively.
        filter_overrides = {
             GeometryField: {
                 'filter_class': CharFilter
             }
        }


class SourceFilter(rest_framework_filters.FilterSet):
    """Filter for Sources"""
    instrument = rest_framework_filters.RelatedFilter(
        InstrumentFilter,
        field_name='instrument',
        queryset=geospaas.vocabularies.models.Instrument.objects.all()
    )
    platform = rest_framework_filters.RelatedFilter(
        PlatformFilter,
        field_name='platform',
        queryset=geospaas.vocabularies.models.Platform.objects.all()
    )


class PersonnelFilter(rest_framework_filters.FilterSet):
    """Filter for Personnel objects"""
    class Meta:
        model = geospaas.catalog.models.Personnel
        fields = {
            'phone': '__all__',
            'fax': '__all__',
            'address': '__all__',
            'city': '__all__',
            'province_or_state': '__all__',
            'postal_code': '__all__',
            'country': '__all__'
        }


class RoleFilter(rest_framework_filters.FilterSet):
    """Filter for Roles"""
    personnel = rest_framework_filters.RelatedFilter(
        PersonnelFilter,
        field_name='personnel',
        queryset = geospaas.catalog.models.Personnel.objects.all()
    )
    class Meta:
        model = geospaas.catalog.models.Role
        fields = {'role': '__all__'}


class DatasetFilter(rest_framework_filters.FilterSet):
    """Filter for Datasets"""
    iso_topic_category = rest_framework_filters.RelatedFilter(
        ISOTopicCategoryFilter,
        field_name='ISO_topic_category',
        queryset=geospaas.vocabularies.models.ISOTopicCategory.objects.all()
    )
    data_center = rest_framework_filters.RelatedFilter(
        DataCenterFilter,
        field_name='data_center',
        queryset=geospaas.vocabularies.models.DataCenter.objects.all()
    )
    source = rest_framework_filters.RelatedFilter(
        SourceFilter,
        field_name='source',
        queryset=geospaas.catalog.models.Source.objects.all()
    )
    geographic_location = rest_framework_filters.RelatedFilter(
        GeographicLocationFilter,
        field_name='geographic_location',
        queryset=geospaas.catalog.models.GeographicLocation.objects.all()
    )
    gcmd_location = rest_framework_filters.RelatedFilter(
        LocationFilter,
        field_name='gcmd_location',
        queryset=geospaas.vocabularies.models.Location.objects.all()
    )
    parameters = rest_framework_filters.RelatedFilter(
        ParameterFilter,
        field_name='parameters',
        queryset=geospaas.vocabularies.models.Parameter.objects.all()
    )

    class Meta:
        model = geospaas.catalog.models.Dataset
        fields = {
            'id': ['exact'],
            'entry_id': ['exact'],
            'entry_title': '__all__',
            'summary': '__all__',
            'time_coverage_start': '__all__',
            'time_coverage_end': '__all__',
            'access_constraints': '__all__'
        }


class DatasetURIFilter(rest_framework_filters.FilterSet):
    """Filter for DatasetURIs"""
    dataset = rest_framework_filters.RelatedFilter(
        DatasetFilter,
        field_name='dataset',
        queryset=geospaas.catalog.models.Dataset.objects.all()
    )
    class Meta:
        model = geospaas.catalog.models.DatasetURI
        fields = {
            'name': '__all__',
            'service': '__all__',
            'uri': '__all__',
        }


class DatasetRelationshipFilter(rest_framework_filters.FilterSet):
    """Filter for DatasetRelationships"""
    child = rest_framework_filters.RelatedFilter(
        DatasetFilter,
        field_name='child',
        queryset=geospaas.catalog.models.Dataset.objects.all()
    )
    parent = rest_framework_filters.RelatedFilter(
        DatasetFilter,
        field_name='parent',
        queryset=geospaas.catalog.models.Dataset.objects.all()
    )
