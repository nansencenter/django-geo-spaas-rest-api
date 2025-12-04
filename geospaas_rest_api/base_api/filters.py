"""Custom filters for the base geospaas API"""
import rest_framework_filters
from django.contrib.gis.db.models import GeometryField, JSONField
from django_filters.rest_framework.filters import CharFilter

import geospaas.catalog.models
import geospaas.vocabularies.models


class KeywordFilter(rest_framework_filters.FilterSet):
    """Filter for Keywords"""
    class Meta:
        model = geospaas.vocabularies.models.Keyword
        fields = {
            'version': '__all__',
            'kind': '__all__',
            'data': '__all__',
        }
        filter_overrides = {JSONField: {'filter_class': CharFilter}}


class ParameterFilter(rest_framework_filters.FilterSet):
    """Filter for Parameters"""
    gcmd_science_keyword = rest_framework_filters.RelatedFilter(
        KeywordFilter,
        field_name='gcmd_science_keyword',
        queryset=geospaas.vocabularies.models.Keyword.objects.all())
    class Meta:
        model = geospaas.vocabularies.models.Parameter
        fields = {
            'version': '__all__',
            'kind': '__all__',
            'data': '__all__',
        }
        filter_overrides = {JSONField: {'filter_class': CharFilter}}


class TagFilter(rest_framework_filters.FilterSet):
    """Filter for Tags"""

    class Meta:
        model = geospaas.catalog.models.Tag
        fields = {'name': '__all__', 'value': '__all__'}


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
    tags = rest_framework_filters.RelatedFilter(
        TagFilter,
        field_name='tags',
        queryset=geospaas.catalog.models.Tag.objects.all(),
        distinct=True)
    keywords = rest_framework_filters.RelatedFilter(
        KeywordFilter,
        field_name='keywords',
        queryset=geospaas.vocabularies.models.Keyword.objects.all(),
        distinct=True)
    parameters = rest_framework_filters.RelatedFilter(
        ParameterFilter,
        field_name='parameters',
        queryset=geospaas.vocabularies.models.Parameter.objects.all(),
        distinct=True)

    class Meta:
        model = geospaas.catalog.models.Dataset
        fields = {
            'id': '__all__',
            'entry_id': '__all__',
            'entry_title': '__all__',
            'summary': '__all__',
            'time_coverage_start': '__all__',
            'time_coverage_end': '__all__',
            'access_constraints': '__all__',
            'location': '__all__',
        }
        filter_overrides = {GeometryField: {'filter_class': CharFilter}}


class DatasetURIFilter(rest_framework_filters.FilterSet):
    """Filter for DatasetURIs"""
    dataset = rest_framework_filters.RelatedFilter(
        DatasetFilter,
        field_name='dataset',
        queryset=geospaas.catalog.models.Dataset.objects.all()
    )
    class Meta:
        model = geospaas.catalog.models.DatasetURI
        fields = {'uri': '__all__'}


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
