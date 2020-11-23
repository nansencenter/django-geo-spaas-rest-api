"""Tests for the read-only part of the GeoSPaaS REST API"""
import unittest.mock as mock

import django.test
import rest_framework.request
import rest_framework.views

import geospaas_rest_api.filters
import geospaas_rest_api.views


class BasicAPITests(django.test.TestCase):
    """Basic API testing to receive 200 responses and some exact responses"""
    fixtures = ["read_only_tests_data"]

    def test_api_root_call(self):
        """shall return status code 200 for root"""
        response = self.client.get('/api/')
        self.assertEqual(response.status_code, 200)

    def test_geographic_locations_call(self):
        """
        shall return status code 200 for geographic_locations as well as exact geographic_locations
        """
        response2 = self.client.get('/api/geographic_locations/')
        self.assertEqual(response2.status_code, 200)
        self.assertJSONEqual(response2.content, {
            'next': None, 'previous': None, 'results': [
                {'id': 1, 'geometry': 'SRID=4326;POLYGON ((0 0, 0 10, 10 10, 10 0, 0 0))'},
                {'id': 2, 'geometry': 'SRID=4326;POLYGON ((20 20, 20 30, 30 30, 30 20, 20 20))'}
            ]
        })

    def test_sources_call(self):
        """shall return status code 200 for source as well as exact source object"""
        response3 = self.client.get('/api/sources/1/')
        self.assertEqual(response3.status_code, 200)
        self.assertJSONEqual(response3.content,
                             {'id': 1, 'specs': 'Nothing special', 'platform': 1, 'instrument': 2})

    def test_instruments_call(self):
        """shall return status code 200 for instruments as well as exact instrument object"""
        response4 = self.client.get('/api/instruments/2/')
        self.assertEqual(response4.status_code, 200)
        self.assertJSONEqual(response4.content, {
            'id': 2, 'category': 'Solar/Space Observing Instruments',
            'instrument_class': 'X-Ray/Gamma Ray Detectors',
            'type': 'dummy_included_in_test_mode',
            'subtype': 'dummy_included_in_test_mode',
            'short_name': 'HXT',
            'long_name': 'Hard X-ray Telescope'
        })

    def test_platforms_call(self):
        """shall return status code 200 for platforms as well as exact platform object"""
        response5 = self.client.get('/api/platforms/2/')
        self.assertEqual(response5.status_code, 200)
        self.assertJSONEqual(response5.content, {
            'id': 2, 'category': 'Aircraft',
            'series_entity': 'dummy_included_in_test_mode',
            'short_name': 'A340-600',
            'long_name': 'Airbus A340-600'
        })

    def test_datasets_call(self):
        """shall return status code 200 for datasets as well as exact dataset object"""
        response8 = self.client.get('/api/datasets/1/')
        self.assertEqual(response8.status_code, 200)
        self.assertJSONEqual(response8.content, {
            'id': 1,
            'entry_id': 'NERSC_test_dataset_titusen',
            'entry_title': 'Test dataset',
            'summary': 'This is a quite short summary about the test dataset.',
            'time_coverage_start': '2010-01-01T00:00:00Z',
            'time_coverage_end': '2010-01-02T00:00:00Z',
            'access_constraints': None,
            'ISO_topic_category': 1,
            'data_center': 1,
            'source': 1,
            'geographic_location': 1,
            'gcmd_location': 1,
            'parameters': []
        })

    def test_parameters_call(self):
        """shall return status code 200 for parameters"""
        response9 = self.client.get('/api/parameters/')
        self.assertEqual(response9.status_code, 200)

    def test_dataset_uris_call(self):
        """shall return status code 200 for dataset_uri as well as exact dataset_uri object"""
        response10 = self.client.get('/api/dataset_uris/2/')
        self.assertEqual(response10.status_code, 200)
        self.assertJSONEqual(response10.content, {
            'id': 2,
            'name': 'fileService',
            'service': 'local',
            'uri': 'file://localhost/some/test/file2.ext',
            'dataset': 2
        })

    def test_dataset_relationships_call(self):
        """shall return status code 200 for dataset_relationships"""
        response11 = self.client.get('/api/dataset_relationships/')
        self.assertEqual(response11.status_code, 200)

    def test_datacenters_call(self):
        """shall return status code 200 for datacenters as well as exact datacenter object"""
        response12 = self.client.get('/api/datacenters/2/')
        self.assertEqual(response12.status_code, 200)
        self.assertJSONEqual(response12.content, {
            'id': 2,
            'bucket_level0': 'ACADEMIC',
            'bucket_level1': 'dummy_included_in_test_mode',
            'bucket_level2': 'dummy_included_in_test_mode',
            'bucket_level3': 'dummy_included_in_test_mode',
            'short_name': 'AALTO',
            'long_name': 'Aalto University',
            'data_center_url': 'dummy_included_in_test_mode'
        })
