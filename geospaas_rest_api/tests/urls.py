"""geospaas_rest_api testing URL Configuration"""

from django.conf.urls import include, url

urlpatterns = [
    url(r'^', include('geospaas.urls')),
    url(r'^api/', include('geospaas_rest_api.urls')),
]
