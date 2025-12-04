"""Tests for the read-only part of the GeoSPaaS REST API"""
import django.test


class BasicAPITests(django.test.TestCase):
    """Basic API testing to receive 200 responses and some exact responses"""
    fixtures = ["read_only_tests_data"]

    def test_api_root_call(self):
        """shall return status code 200 for root"""
        response = self.client.get('/api/')
        self.assertEqual(response.status_code, 200)

    def test_keyword_call(self):
        """shall return status code 200 for and a serialized keyword"""
        response3 = self.client.get('/api/keywords/1/')
        self.assertEqual(response3.status_code, 200)
        self.assertJSONEqual(
            response3.content,
            {
                "id":1,
                "version": "",
                "kind": "gcmd_instrument",
                "data": {
                    "category": "Earth Remote Sensing Instruments",
                    "short_name":"",
                    "long_name":"",
                    "subtype":"",
                    "type":"",
                    "instrument_class":""
                }
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
            'keywords': [2, 18, 3, 7, 17],
            'location': ("SRID=4326;POLYGON ((0 0, 0 10, 10 10, 10 0, 0 0))"),
            'parameters': [],
            'tags': [],
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
            'uri': 'file://localhost/some/test/file2.ext',
            'dataset': 2
        })

    def test_dataset_relationships_call(self):
        """shall return status code 200 for dataset_relationships"""
        response11 = self.client.get('/api/dataset_relationships/')
        self.assertEqual(response11.status_code, 200)


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
        'keywords': [2, 18, 3, 7, 17],
        'location': ("SRID=4326;POLYGON ((0 0, 0 10, 10 10, 10 0, 0 0))"),
        'parameters': [],
        'tags': [],
    }

    DATASET_DICT_2 = {
        'id': 2,
        'entry_id': 'NERSC_test_dataset_tjuetusen',
        'entry_title': 'Test child dataset',
        'summary': 'This is a quite short summary about the test dataset.',
        'time_coverage_start': '2010-01-02T00:00:00Z',
        'time_coverage_end': '2010-01-03T00:00:00Z',
        'access_constraints': None,
        'keywords': [2, 18, 4, 8, 17],
        'location': ("SRID=4326;POLYGON ((20 20, 20 30, 30 30, 30 20, 20 20))"),
        'parameters': [],
        'tags': [],
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
            '/api/datasets/?location__intersects=POINT+%289+9%29')
        self.assertJSONEqual(
            response.content,
            {'next': None, 'previous': None, 'results': [self.DATASET_DICT_1]})

        # giving a location with SRID
        response = self.client.get(
            '/api/datasets/'
            '?location__intersects=SRID%3D4326%3BPOINT+%289+9%29'
        )
        self.assertJSONEqual(
            response.content,
            {'next': None, 'previous': None, 'results': [self.DATASET_DICT_1]})

    def test_source_instrument_filtering(self):
        """Test filtering datasets on their instrument"""
        response = self.client.get('/api/datasets/?keywords__data__icontains=HXT')
        self.assertJSONEqual(response.content, {
            'next': None, 'previous': None, 'results': [self.DATASET_DICT_1, self.DATASET_DICT_2]})

    def test_source_platform_filtering(self):
        """Test filtering datasets on a keyword which should be
        contained in the platform short name
        """
        response = self.client.get('/api/datasets/?keywords__data__icontains=A340')
        self.assertJSONEqual(response.content, {
            'next': None, 'previous': None, 'results': [self.DATASET_DICT_2]
        })

    def test_source_filtering(self):
        """Test filtering datasets on their platform and instrument"""
        self.maxDiff = None
        response = self.client.get(
            '/api/datasets/'
            '?keywords__data__icontains=A340-600')
        self.assertJSONEqual(
            response.content,
            {'next': None, 'previous': None, 'results': [self.DATASET_DICT_2]})

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
            '&location__contains=POINT+%289+9%29'
            '&keywords__data__short_name__contains=HXT'
        )
        self.assertJSONEqual(
            response.content,
            {'next': None, 'previous': None, 'results': [self.DATASET_DICT_1]})


class DatasetURIFilteringTests(django.test.TestCase):
    """Tests dataset URIs filtering based on diverse parameters"""

    fixtures = ["read_only_tests_data"]

    def test_dataset_id_filtering(self):
        """Test filtering dataset URIs on a dataset ID"""
        response = self.client.get('/api/dataset_uris/?dataset=1')
        self.assertJSONEqual(response.content, {
            'next': None, 'previous': None, 'results': [{
                "id": 1,
                "uri": "file://localhost/some/test/file1.ext",
                "dataset": 1
            }]
        })
