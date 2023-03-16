"""Django models"""
try:
    import geospaas_processing
except ImportError:
    geospaas_processing = None

from .base import Job

if geospaas_processing:
    from .processing_jobs import (DownloadJob,
                                  ConvertJob,
                                  SyntoolCleanupJob,
                                  HarvestJob)
