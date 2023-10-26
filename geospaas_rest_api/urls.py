# pylint: disable=ungrouped-imports
"""geospaas_rest_api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import os

import geospaas_rest_api.base_api.views as base_views
from rest_framework import routers


router = routers.DefaultRouter()

router.register(r'datacenters', base_views.DataCenterViewSet)
router.register(r'dataset_relationships', base_views.DatasetRelationshipViewSet)
router.register(r'dataset_uris', base_views.DatasetURIViewSet)
router.register(r'datasets', base_views.DatasetViewSet)
router.register(r'gcmd_locations', base_views.LocationViewSet)
router.register(r'geographic_locations', base_views.GeographicLocationViewSet)
router.register(r'instruments', base_views.InstrumentViewSet)
router.register(r'parameters', base_views.ParameterViewSet)
router.register(r'platforms', base_views.PlatformViewSet)
router.register(r'science_keywords', base_views.ScienceKeywordViewSet)
router.register(r'sources', base_views.SourceViewSet)
if os.environ.get('GEOSPAAS_REST_API_ENABLE_PROCESSING', 'false').lower() == 'true':
    import geospaas_rest_api.processing_api.views as processing_views
    router.register(r'tasks', processing_views.TaskViewSet)
    router.register(r'jobs', processing_views.JobViewSet)
    router.register(r'processing_results', processing_views.ProcessingResultViewSet)

urlpatterns = router.urls
