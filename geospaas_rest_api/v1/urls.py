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

from rest_framework import routers
from geospaas_rest_api.v1 import views


router = routers.DefaultRouter()

router.register(r'geographic_locations', views.GeographicLocationViewSet, 'v1')
router.register(r'sources', views.SourceViewSet, 'v1')
router.register(r'instruments', views.InstrumentViewSet, 'v1')
router.register(r'platforms', views.PlatformViewSet, 'v1')
router.register(r'people', views.PersonnelViewSet, 'v1')
router.register(r'roles', views.RoleViewSet, 'v1')
router.register(r'datasets', views.DatasetViewSet, 'v1')
router.register(r'parameters', views.ParameterViewSet, 'v1')
router.register(r'dataset_uris', views.DatasetURIViewSet, 'v1')
router.register(r'dataset_relationships', views.DatasetRelationshipViewSet, 'v1')
router.register(r'datacenters', views.DataCenterViewSet, 'v1')
if os.environ.get('GEOSPAAS_REST_API_ENABLE_PROCESSING', 'false').lower() == 'true':
    router.register(r'tasks', views.TaskViewSet, 'v1')
    router.register(r'jobs', views.JobViewSet, 'v1')

urlpatterns = router.urls
