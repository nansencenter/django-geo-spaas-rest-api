"""Django models"""
try:
    import geospaas_processing
except ImportError:  # pragma: no cover
    geospaas_processing = None

if geospaas_processing:
    from .processing_api.models import (Job,
                                        DownloadJob,
                                        ConvertJob,
                                        SyntoolCleanupJob,
                                        HarvestJob)
