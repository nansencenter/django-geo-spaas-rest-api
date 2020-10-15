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
from rest_framework import routers
from geospaas_rest_api import views


router = routers.DefaultRouter()

router.register(r'geographic_locations', views.GeographicLocationViewSet)
router.register(r'sources', views.SourceViewSet)
router.register(r'instruments', views.InstrumentViewSet)
router.register(r'platforms', views.PlatformViewSet)
router.register(r'people', views.PersonnelViewSet)
router.register(r'roles', views.RoleViewSet)
router.register(r'datasets', views.DatasetViewSet)
router.register(r'parameters', views.ParameterViewSet)
router.register(r'dataset_uris', views.DatasetURIViewSet)
router.register(r'dataset_relationships', views.DatasetRelationshipViewSet)
router.register(r'datacenters', views.DataCenterViewSet)

urlpatterns = router.urls
