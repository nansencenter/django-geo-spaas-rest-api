"""Tests for the Django apps"""
import django.apps
import django.test

import geospaas_rest_api.apps

class GeospaasRestApiAppTestCase(django.test.SimpleTestCase):
    """Test the geospaas_rest_api app"""
    def test_app_name(self):
        """Test the app has the correct name"""
        app_name = 'geospaas_rest_api'
        self.assertEqual(geospaas_rest_api.apps.GeospaasRestApiConfig.name, app_name)
