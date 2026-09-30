"""geospaas_rest_api testing URL Configuration"""

from django.urls import include, re_path

urlpatterns = [
    re_path(r'^', include('geospaas.urls')),
    re_path(r'^api/', include('geospaas_rest_api.urls')),
]
