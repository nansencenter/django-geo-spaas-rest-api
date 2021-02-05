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


class DatasetFilteringTests(django.test.TestCase):
    """Tests dataset filtering based on diverse parameters"""
    fixtures = ["read_only_tests_data"]

    DATASET_DICT_1 = {
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
    }

    DATASET_DICT_2 = {
        'id': 2,
        'entry_id': 'NERSC_test_dataset_tjuetusen',
        'entry_title': 'Test child dataset',
        'summary': 'This is a quite short summary about the test dataset.',
        'time_coverage_start': '2010-01-02T00:00:00Z',
        'time_coverage_end': '2010-01-03T00:00:00Z',
        'access_constraints': None,
        'ISO_topic_category': 1,
        'data_center': 2,
        'source': 2,
        'geographic_location': 2,
        'gcmd_location': 1,
        'parameters': []
    }

    def test_time_filtering(self):
        """Test filtering with a date that should be in the dataset time coverage"""
        date = '2010-01-02 01:00:00Z'
        response = self.client.get(
            f'/api/datasets/?time_coverage_start__lte={date}&time_coverage_end__gte={date}')
        self.assertJSONEqual(response.content, {
            'next': None, 'previous': None, 'results': [self.DATASET_DICT_2]
        })

    def test_time_range_filtering(self):
        """Test filtering with a time range which should intersect with the dataset time coverage"""
        time_range_start = '2010-01-01T01:00:00Z'
        time_range_end = '2010-01-02T01:00:00Z'
        response = self.client.get(
            '/api/datasets/'
            f'?time_coverage_start__lte={time_range_end}'
            f'&time_coverage_end__gte={time_range_start}'
        )
        self.assertJSONEqual(response.content, {
            'next': None, 'previous': None, 'results':[self.DATASET_DICT_1, self.DATASET_DICT_2]
        })

    def test_time_filtering_error_400_on_wrong_date_format(self):
        """
        An error 400 should be returned if the format of the date provided to the filter is invalid
        """
        response = self.client.get('/api/datasets/?time_coverage_start__lte=2010-01-02T01:00:Z')
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(
            response.content,
            {"time_coverage_start__lte": ["Enter a valid date/time."]}
        )

    def test_time_filtering_with_naive_datetime(self):
        """In case a naive date is provided to the filter, it should be considered as UTC time"""
        time_range_start = '2010-01-01T01:00:00Z'
        time_range_end = '2010-01-02T01:00:00'
        response = self.client.get(
            '/api/datasets/'
            f'?time_coverage_start__lte={time_range_end}'
            f'&time_coverage_end__gte={time_range_start}'
        )
        self.assertJSONEqual(response.content, {
            'next': None, 'previous': None, 'results': [self.DATASET_DICT_1, self.DATASET_DICT_2]
        })

    def test_zone_filtering(self):
        """Test filtering datasets on geographic location using a WKT string.
        If no SRID is specified, 4326 should be assumed.
        """
        # giving a location without SRID
        response = self.client.get(
            '/api/datasets/?geographic_location__geometry__intersects=POINT+%289+9%29')
        self.assertJSONEqual(response.content, {
            'next': None, 'previous': None, 'results': [self.DATASET_DICT_1]
        })

        # giving a location with SRID
        response = self.client.get(
            '/api/datasets/'
            '?geographic_location__geometry__intersects=SRID%3D4326%3BPOINT+%289+9%29'
        )
        self.assertJSONEqual(response.content, {
            'next': None, 'previous': None, 'results': [self.DATASET_DICT_1]
        })

    def test_source_instrument_filtering(self):
        """Test filtering datasets on their instrument"""
        response = self.client.get('/api/datasets/?source__instrument__short_name=HXT')
        self.assertJSONEqual(response.content, {
            'next': None, 'previous': None, 'results': [self.DATASET_DICT_1, self.DATASET_DICT_2]}
        )

    def test_source_platform_filtering(self):
        """Test filtering datasets on a keyword which should be
        contained in the platform short name
        """
        response = self.client.get('/api/datasets/?source__platform__short_name__contains=A340')
        self.assertJSONEqual(response.content, {
            'next': None, 'previous': None, 'results': [self.DATASET_DICT_2]
        })

    def test_source_filtering(self):
        """Test filtering datasets on their platform and instrument"""
        response = self.client.get(
            '/api/datasets/'
            '?source__platform__short_name=A340-600'
            '&source__instrument__short_name=HXT')
        self.assertJSONEqual(response.content, {
            'next': None, 'previous': None, 'results': [self.DATASET_DICT_2]
        })

    def test_zone_and_time_filtering(self):
        """Test filtering datasets on both time and location"""
        date = '2010-01-01T07%3A00%3A00Z'
        response = self.client.get(
            '/api/datasets/'
            f'?time_coverage_start__lte={date}&time_coverage_end__gte={date}'
            '&geographic_location__geometry__contains=POINT+%289+9%29'
        )
        self.assertJSONEqual(response.content, {
            'next': None, 'previous': None, 'results': [self.DATASET_DICT_1]}
        )

    def test_zone_source_and_time_filtering(self):
        """Test filtering datasets based on time, source and zone simultaneously"""
        date = '2010-01-01T07%3A00%3A00Z'
        response = self.client.get(
            '/api/datasets/'
            f'?time_coverage_start__lte={date}&time_coverage_end__gte={date}'
            '&geographic_location__geometry__contains=POINT+%289+9%29'
            '&source__instrument__short_name__contains=HXT'
        )
        self.assertJSONEqual(response.content, {
            'next': None, 'previous': None, 'results': [self.DATASET_DICT_1]}
        )

    def test_invalid_direct_lookup(self):
        """An error must happen when an invalid lookup is submitted
        on a "direct" (i.e. not related) filter
        """
        response = self.client.get('/api/datasets/?entry_id__contai=titusen')
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, ["Invalid lookups found: ['entry_id__contai']"])


    def test_invalid_related_lookup(self):
        """An error must happen when an invalid lookup is submitted
        on a related filter
        """
        response = self.client.get('/api/datasets/?source__instrument__short_name__foo=HXT')
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, [
            "Invalid lookups found: ['source__instrument__short_name__foo']"
        ])

    def test_invalid_lookup_multiple_parameters(self):
        """An error must happen when an invalid lookup is submitted
        on a filter, even when other parameters are present
        """
        response = self.client.get(
            '/api/datasets/?entry_id__contai=titusen'
            '&summary__contains=test'
        )
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, ["Invalid lookups found: ['entry_id__contai']"])

    def test_invalid_exact_lookup(self):
        """An error must happen when an invalid "exact" lookup
        is submitted
        """
        response = self.client.get('/api/datasets/?sourc=1')
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, [
            "Invalid lookups found: ['sourc']"
        ])


class DatasetURIFilteringTests(django.test.TestCase):
    """Tests dataset URIs filtering based on diverse parameters"""

    fixtures = ["read_only_tests_data"]

    def test_dataset_id_filtering(self):
        """Test filtering dataset URIs on a dataset ID"""
        response = self.client.get('/api/dataset_uris/?dataset=1')
        self.assertJSONEqual(response.content, {
            'next': None, 'previous': None, 'results': [{
                "id": 1,
                "name": "fileService",
                "service": "local",
                "uri": "file://localhost/some/test/file1.ext",
                "dataset": 1
            }]
        })
