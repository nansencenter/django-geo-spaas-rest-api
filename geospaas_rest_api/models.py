"""Django models"""
try:
    import geospaas_processing
except ImportError:  # pragma: no cover
    geospaas_processing = None

if geospaas_processing:
    from geospaas_rest_api.processing_api.models import (Job,
                                                         DownloadJob,
                                                         ConvertJob,
                                                         SyntoolCleanupJob,
                                                         SyntoolCompareJob,
                                                         HarvestJob,
                                                         WorkdirCleanupJob)
