from django.test import TestCase
from django.test import Client
from geospaas.vocabularies.models import Platform, Instrument
from geospaas.vocabularies.models import Parameter, DataCenter
import json

# Create your tests here.


class BasicAPITests(TestCase):
    """basic api testing to receive 200 responses and some reponses"""

    fixtures = ["vocabularies", "catalog"]

    def setUp(self):
        self.c = Client()

    def test_api_root_calls(self):
        """shall return status code 200 for root"""
        response = self.c.get('//api/')
        self.assertEqual(response.status_code, 200)

    def test_geographic_locations_call(self):
        """shall return status code 200 for geographic_locations as well as ........................"""
        response2 = self.c.get('//api/geographic_locations/')
        self.assertEqual(response2.status_code, 200)
        self.assertEqual([{'id': 1, 'geometry': 'SRID=4326;POLYGON ((0 0, 0 10, 10 10, 10 0, 0 0))'},
                          {'id': 2, 'geometry': 'SRID=4326;POLYGON ((20 20, 20 30, 30 30, 30 20, 20 20))'}],
                         json.loads(response2.content))

    def test_api_initial_sources_call(self):
        """basic api testing to receive some responses
        for sources"""
        response3 = self.c.get('//api/sources/1/')
        self.assertEqual(response3.status_code, 200)
        self.assertEqual({'id': 1, 'specs': 'Nothing special', 'platform': 1, 'instrument': 2},
                         json.loads(response3.content))

    def test_api_initial_instruments_call(self):
        """basic api testing to receive some responses
        for instruments"""
        response4 = self.c.get('//api/instruments/2/')
        self.assertEqual(response4.status_code, 200)
        self.assertEqual({'id': 2, 'category': 'Solar/Space Observing Instruments',
                          'instrument_class': 'X-Ray/Gamma Ray Detectors',
                          'type': 'dummy_included_in_test_mode',
                          'subtype': 'dummy_included_in_test_mode',
                          'short_name': 'HXT',
                          'long_name': 'Hard X-ray Telescope'},
                         json.loads(response4.content))

    def test_api_initial_platforms_call(self):
        """basic api testing to receive some responses
        for platforms"""
        response5 = self.c.get('//api/platforms/2/')
        self.assertEqual(response5.status_code, 200)
        self.assertEqual({'id': 2, 'category': 'Aircraft',
                          'series_entity': 'dummy_included_in_test_mode',
                          'short_name': 'A340-600', 'long_name': 'Airbus A340-600'},
                         json.loads(response5.content))

    def test_api_initial_people_call(self):
        """shall return status code 200 for people"""
        response6 = self.c.get('//api/people/')
        self.assertEqual(response6.status_code, 200)

    def test_api_initial_roles_call(self):
        """shall return status code 200 for roles"""
        response7 = self.c.get('//api/roles/')
        self.assertEqual(response7.status_code, 200)

    def test_api_initial_datasets_call(self):
        """basic api testing to receive some responses
        for datasets"""
        response8 = self.c.get('//api/datasets/1/')
        self.assertEqual(response8.status_code, 200)
        self.assertEqual({'id': 1, 'entry_id': 'NERSC_test_dataset_titusen',
                          'entry_title': 'Test dataset',
                          'summary': 'This is a quite short summary about the test dataset.',
                          'time_coverage_start': '2010-01-01T00:00:00Z',
                          'time_coverage_end': '2010-01-02T00:00:00Z',
                          'access_constraints': None,
                          'ISO_topic_category': 1,
                          'data_center': 1, 'source': 1, 'geographic_location': 1,
                          'gcmd_location': 1, 'parameters': []},
                         json.loads(response8.content))

    def test_api_initial_dataset_parameters_call(self):
        """shall return status code 200 for dataset_parameters"""
        response9 = self.c.get('//api/dataset_parameters/')
        self.assertEqual(response9.status_code, 200)

    def test_api_initial_dataset_uris_call(self):
        """basic api testing to receive some responses
        for dataset_uris"""
        response10 = self.c.get('//api/dataset_uris/2/')
        self.assertEqual(response10.status_code, 200)
        self.assertEqual({'id': 2, 'name': 'fileService',
                          'service': 'local', 'uri': 'file://localhost/some/test/file2.ext',
                          'dataset': 2},
                         json.loads(response10.content))

    def test_dataset_relationships_call(self):
        """shall return status code 200 for dataset_relationships"""
        response11 = self.c.get('//api/dataset_relationships/')
        self.assertEqual(response11.status_code, 200)

    def test_api_initial_datacenters_call(self):
        """basic api testing to receive some responses
        for datacenters"""
        response12 = self.c.get('//api/datacenters/2/')
        self.assertEqual(response12.status_code, 200)
        self.assertEqual({'id': 2, 'bucket_level0': 'ACADEMIC',
                          'bucket_level1': 'dummy_included_in_test_mode',
                          'bucket_level2': 'dummy_included_in_test_mode',
                          'bucket_level3': 'dummy_included_in_test_mode',
                          'short_name': 'AALTO', 'long_name': 'Aalto University',
                          'data_center_url': 'dummy_included_in_test_mode'},
                         json.loads(response12.content))


class TimeFilteringAbilityForAPI(TestCase):
    '''time-filtering '''
    fixtures = ["vocabularies", "catalog"]

    def test_time_intervals_for_api(self):
        ''' to test if there are suitable responses for time-filtering '''
        c = Client()
        response = c.get('//api/datasets/?date=2010-01-02T01:00:00Z')
        self.assertContains(response, 'NERSC_test_dataset_tjuetusen')
        self.assertContains(response, 'Test child dataset')
        self.assertEqual([{'id': 2, 'entry_id': 'NERSC_test_dataset_tjuetusen',
                           'entry_title': 'Test child dataset',
                           'summary': 'This is a quite short summary about the test dataset.',
                           'time_coverage_start': '2010-01-02T00:00:00Z',
                           'time_coverage_end': '2010-01-03T00:00:00Z',
                           'access_constraints': None,
                           'ISO_topic_category': 1, 'data_center': 2, 'source': 1,
                           'geographic_location': 2, 'gcmd_location': 1, 'parameters': []}],
                         json.loads(response.content))


class LocationFilteringAbilityForAPI(TestCase):
    '''location-filtering '''
    fixtures = ["vocabularies", "catalog"]

    def test_zone_for_api(self):
        ''' to test if there are suitable responses for location-filtering '''
        c = Client()
        response = c.get('//api/datasets/?zone=POINT+%289+9%29')
        # giving a location without SRID
        self.assertEqual([{'id': 1, 'entry_id': 'NERSC_test_dataset_titusen',
                           'entry_title': 'Test dataset',
                           'summary': 'This is a quite short summary about the test dataset.',
                           'time_coverage_start': '2010-01-01T00:00:00Z',
                           'time_coverage_end': '2010-01-02T00:00:00Z', 'access_constraints': None,
                           'ISO_topic_category': 1, 'data_center': 1, 'source': 1,
                           'geographic_location': 1, 'gcmd_location': 1, 'parameters': []}],
                         json.loads(response.content))
        # giving a location with SRID
        # this example is for SRID=4326;POINT (9 9)
        response2 = c.get('//api/datasets/?zone=SRID%3D4326%3BPOINT+%289+9%29')
        self.assertEqual([{'id': 1, 'entry_id': 'NERSC_test_dataset_titusen',
                           'entry_title': 'Test dataset',
                           'summary': 'This is a quite short summary about the test dataset.',
                           'time_coverage_start': '2010-01-01T00:00:00Z',
                           'time_coverage_end': '2010-01-02T00:00:00Z', 'access_constraints': None,
                           'ISO_topic_category': 1, 'data_center': 1, 'source': 1,
                           'geographic_location': 1, 'gcmd_location': 1, 'parameters': []}],
                         json.loads(response2.content))


class FilteringAbilityForZoneAndTimeSimultaneously(TestCase):
    '''simultaneous-filtering(time and location) '''
    fixtures = ["vocabularies", "catalog"]

    def test_zone_and_time_filtering_simultaneously(self):
        ''' to test if there are suitable responses for
        simultaneous-filtering(time and location) '''
        c = Client()
        response = c.get('//api/datasets/?date= \
            2010-01-01T07%3A00%3A00Z&zone=POINT+%289+9%29')
        self.assertEqual([{'id': 1, 'entry_id': 'NERSC_test_dataset_titusen',
                           'entry_title': 'Test dataset',
                           'summary': 'This is a quite short summary about the test dataset.',
                           'time_coverage_start': '2010-01-01T00:00:00Z',
                           'time_coverage_end': '2010-01-02T00:00:00Z', 'access_constraints': None,
                           'ISO_topic_category': 1, 'data_center': 1, 'source': 1,
                           'geographic_location': 1, 'gcmd_location': 1, 'parameters': []}],
                         json.loads(response.content))
