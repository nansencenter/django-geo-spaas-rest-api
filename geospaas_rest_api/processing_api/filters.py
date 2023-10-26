"""Custom filters for the processing API"""
import geospaas.catalog.models
import geospaas_processing.models
import rest_framework_filters

from ..base_api.filters import DatasetFilter


class ProcessingResultFilter(rest_framework_filters.FilterSet):
    """Filter for ProcessingResults"""
    dataset = rest_framework_filters.RelatedFilter(
        DatasetFilter,
        field_name='dataset',
        queryset=geospaas.catalog.models.Dataset.objects.all()
    )
    class Meta:
        model = geospaas_processing.models.ProcessingResult
        fields = {
            'path': '__all__',
            'type': '__all__',
            'created': '__all__',
        }
