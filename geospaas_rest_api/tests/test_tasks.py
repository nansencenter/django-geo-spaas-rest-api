"""Tests for the long-running tasks endpoint of the GeoSPaaS REST API"""
import os
import unittest.mock as mock

import django.test
from django.http import Http404
from django.http.request import HttpRequest
from django_celery_results.models import TaskResult
from rest_framework.request import Request
from rest_framework.exceptions import ErrorDetail, ValidationError

import geospaas_rest_api.serializers as serializers
import geospaas_rest_api.views as views


os.environ.setdefault('GEOSPAAS_REST_API_ENABLE_PROCESSING', 'true')


class TaskViewSetTests(django.test.TestCase):
    """Test tasks/ endpoints"""

    fixtures = ['processing_tests_data']

    def setUp(self):
        # This mock is necessary to avoid disabling the TaskViewSet when tests are run in an
        # environment where geospaas_processing is not installed.
        mock.patch('geospaas_rest_api.serializers.tasks').start()
        self.addCleanup(mock.patch.stopall)

    def test_tasks_inaccessible_if_geospaas_processing_not_importable(self):
        """
        If geospaas_processing is not importable, the 'tasks/' endpoint should not be accessible
        """
        with mock.patch('geospaas_rest_api.serializers.tasks', None):
            self.assertEqual(self.client.get('/api/tasks/').status_code, 404)
            self.assertEqual(self.client.post('/api/tasks/', {}).status_code, 404)
            self.assertEqual(self.client.get('/api/tasks/1234').status_code, 404)

    def test_launch_task_returns_url(self):
        """When a task is launched, its URL in the API must be returned"""
        task_id = '1234'
        with mock.patch('geospaas_rest_api.serializers.TaskResultSerializer') as ts_mock:
            result_mock = mock.MagicMock()
            result_mock.id = task_id
            ts_mock.return_value.save.return_value = result_mock

            response = self.client.post('/api/tasks/', {
                'action': 'download',
                'parameters': {
                    'dataset_id': 1
                }
            })
        self.assertEqual(response.status_code, 202)
        self.assertEqual(
            response.content.decode("utf-8"),
            f'{{"task_url":"http://testserver/api/tasks/{task_id}/"}}'
        )

    def test_launch_task_if_valid_request_data(self):
        """A task must only be launched if the request data was successfully validated"""
        request_data = {'action': 'download', 'parameters': {'dataset_id': 1}}
        with mock.patch.object(serializers.TaskResultSerializer, 'save') as save_mock:
            with mock.patch.object(serializers.TaskResultSerializer, 'validate') as validate_mock:
                save_mock.return_value.id = '1234'
                validate_mock.return_value = request_data
                self.client.post('/api/tasks/', request_data)
                save_mock.assert_called()

    def test_raise_on_failed_validation(self):
        """A ValidationError must be raised if the data is not valid"""
        request = Request(HttpRequest())
        request._data = {'wrong': 'data'} # pylint: disable=protected-access
        view_set = views.TaskViewSet()
        with mock.patch.object(serializers.TaskResultSerializer, 'save') as save_mock:
            save_mock.return_value.id = '1234'
            with self.assertRaises(ValidationError):
                view_set.create(request)

    def test_error_on_invalid_request_data(self):
        """
        A task must not be launched if the request data is invalid,
        and a 400 status code must be returned to the client
        """
        with mock.patch.object(serializers.TaskResultSerializer, 'save') as save_mock:
            with mock.patch.object(serializers.TaskResultSerializer, 'validate') as validate_mock:
                save_mock.return_value.id = '1234'
                validate_mock.side_effect = ValidationError()
                response = self.client.post('/api/tasks/', {})
        save_mock.assert_not_called()
        self.assertEqual(400, response.status_code)

    def test_get_tasks_list(self):
        """Test that the list of tasks can be retrieved"""
        expected_tasks = [
            {
                'task_id': '733d3a63-7a5a-4a1e-8cf0-750ae393dd99',
                'task_name': 'geospaas_processing.tasks.convert_to_idf',
                'result': [
                    1,
                    'ftp://test/sentinel3_olci_l1_efr/S3A_OL_1_EFR____20181213T024322_20181213T024622_20181214T065355_0179_039_089_2340_LN1_O_NT_002.SEN3'
                ],
                'status': 'SUCCESS',
                'task_args': "((1, 'ftp://test/dataset_1_S3A_OL_1_EFR____20181213T024322_20181213T024622_20181214T065355_0179_039_089_2340_LN1_O_NT_002.zip'),)",
                'date_created': '2020-07-16T13:58:22.918000Z',
                'date_done': '2020-07-16T13:58:21.201000Z',
                'meta': {'children': []}
            }, {
                'task_id': '733d3a63-7a5a-4a1e-8cf0-750ae393dd98',
                'task_name': 'geospaas_processing.tasks.convert_to_idf',
                'result': {'pid': 23, 'hostname': 'celery@3b6b6202fcbe'},
                'status': 'STARTED',
                'task_args': "((1, 'ftp://test/dataset_1_S3A_OL_1_EFR____20181213T024322_20181213T024622_20181214T065355_0179_039_089_2340_LN1_O_NT_002.zip'),)",
                'date_created': '2020-07-16T13:57:21.918000Z',
                'date_done': '2020-07-16T13:57:21.918000Z',
                'meta': {'children': []}
            }, {
                'task_id': 'df2bfb58-7d2e-4f83-9dc2-bac95a421c72',
                'task_name': 'geospaas_processing.tasks.download',
                'result': [1, 'ftp://test/dataset_1_S3A_OL_1_EFR____20181213T024322_20181213T024622_20181214T065355_0179_039_089_2340_LN1_O_NT_002.zip'],
                'status': 'SUCCESS',
                'task_args': '(1,)',
                'date_created': '2020-07-16T13:53:33.864000Z',
                'date_done': '2020-07-16T13:57:21.912000Z',
                'meta': {
                    'children': [[['733d3a63-7a5a-4a1e-8cf0-750ae393dd98', None], None]]
                }
            }, {
                'task_id': 'df2bfb58-7d2e-4f83-9dc2-bac95a421c71',
                'task_name': 'geospaas_processing.tasks.download',
                'result': {'pid': 22, 'hostname': 'celery@3b6b6202fcbe'},
                'status': 'STARTED',
                'task_args': '(1,)',
                'date_created': '2020-07-16T13:52:33.864000Z',
                'date_done': '2020-07-16T13:52:33.864000Z',
                'meta': {'children': []}
            }
        ]
        self.assertJSONEqual(self.client.get('/api/tasks/').content, expected_tasks)

    def test_get_task(self):
        """Test that a single task can be retrieved"""
        expected_task = {
            'task_id': 'df2bfb58-7d2e-4f83-9dc2-bac95a421c71',
            'task_name': 'geospaas_processing.tasks.download',
            'result': {'pid': 22, 'hostname': 'celery@3b6b6202fcbe'},
            'status': 'STARTED',
            'task_args': '(1,)',
            'date_created': '2020-07-16T13:52:33.864000Z',
            'date_done': '2020-07-16T13:52:33.864000Z',
            'meta': {'children': []}
        }
        response = self.client.get('/api/tasks/df2bfb58-7d2e-4f83-9dc2-bac95a421c71/')
        self.assertJSONEqual(response.content, expected_task)

    def test_get_pending_status_from_celery(self):
        """Get tasks status from celery if it is not available in the database yet"""
        task_id = '1234'
        with mock.patch.object(views.TaskViewSet, 'get_object', side_effect=Http404):
            with mock.patch('celery.result.AsyncResult') as result_mock:
                result_mock.return_value.status = 'PENDING'
                self.assertEqual(
                    self.client.get(f'/api/tasks/{task_id}/').content.decode('utf-8'),
                    '{"status":"PENDING"}'
                )


class TaskResultSerializerTests(django.test.TestCase):
    """Tests for the TaskResultSerializer"""

    fixtures = ['processing_tests_data']

    def setUp(self):
        tasks_patcher = mock.patch.object(serializers, 'tasks')
        self.tasks_mock = tasks_patcher.start()
        self.addCleanup(mock.patch.stopall)

    def test_error_if_geospaas_processing_not_importable(self):
        """
        It should not be possible to instantiate a TaskResultSerializer
        if geospaas_processing is not importable
        """
        with mock.patch('geospaas_rest_api.serializers.tasks', None):
            with self.assertRaises(ImportError):
                serializers.TaskResultSerializer()

    def test_validation_return_value(self):
        """Test tha the validate() method returns the validated data"""
        request_data = {'action': 'download', 'parameters': {'dataset_id': 1}}
        serializer = serializers.TaskResultSerializer()
        self.assertDictEqual(serializer.validate(request_data), request_data)

    def test_validation_empty_data(self):
        """Validation must fail if the data is an empty dict"""
        serializer = serializers.TaskResultSerializer(data={})
        with self.assertRaises(ValidationError) as assert_raises:
            self.assertFalse(serializer.is_valid(raise_exception=True))
        self.assertDictEqual(
            assert_raises.exception.detail,
            {
                'action': [ErrorDetail(string='This field is required.', code='required')],
                'parameters': [ErrorDetail(string='This field is required.', code='required')]
            }
        )

    def test_validation_no_action_field(self):
        """Validation must fail if the action field is not present"""
        serializer = serializers.TaskResultSerializer(data={'parameters': {}})
        with self.assertRaises(ValidationError) as assert_raises:
            self.assertFalse(serializer.is_valid(raise_exception=True))
        self.assertDictEqual(
            assert_raises.exception.detail,
            {'action': [ErrorDetail(string='This field is required.', code='required')]}
        )

    def test_validation_no_parameter_field(self):
        """Validation must fail if the parameter field is not present"""
        serializer = serializers.TaskResultSerializer(data={'action': 'download'})
        with self.assertRaises(ValidationError) as assert_raises:
            self.assertFalse(serializer.is_valid(raise_exception=True))
        self.assertDictEqual(
            assert_raises.exception.detail,
            {'parameters': [ErrorDetail(string='This field is required.', code='required')]}
        )

    def test_validation_parameter_field_not_dict(self):
        """Validation must fail if the parameter field is not a dictionary"""
        serializer = serializers.TaskResultSerializer(data={'action': 'download', 'parameters': ''})
        with self.assertRaises(ValidationError) as assert_raises:
            self.assertFalse(serializer.is_valid(raise_exception=True))
        self.assertDictEqual(
            assert_raises.exception.detail,
            {
                'parameters': [
                    ErrorDetail(string='Expected a dictionary of items but got type "str".',
                                code='not_a_dict')
                ]
            }
        )

    def test_validate_error_on_wrong_action(self):
        """Validation must fail if an invalid action is requested"""
        serializer = serializers.TaskResultSerializer(data={
            'action': 'wrong_value', 'parameters': {}
        })
        with self.assertRaises(ValidationError) as assert_raises:
            self.assertFalse(serializer.is_valid(raise_exception=True))
        self.assertDictEqual(
            assert_raises.exception.detail,
            {
                'action': [
                    ErrorDetail(string='"wrong_value" is not a valid choice.',
                                code='invalid_choice')
                ]
            }
        )

    def test_validate_error_on_wrong_parameter_key(self):
        """Validation must fail if wrong parameter keys are provided to an action"""
        serializer = serializers.TaskResultSerializer(data={
            'action': 'download', 'parameters': {'wrong_key': 1}
        })
        with self.assertRaises(ValidationError) as assert_raises:
            self.assertFalse(serializer.is_valid(raise_exception=True))
        self.assertDictEqual(
            assert_raises.exception.detail,
            {
                'non_field_errors': [
                    ErrorDetail(
                        string="The valid parameters for the 'download' action are: ['dataset_id']",
                        code='invalid'
                    )
                ]
            }
        )

    def test_validate_error_on_wrong_parameter_value_type(self):
        """Validation must fail if the wrong type of parameter value is provided to an action"""
        serializer = serializers.TaskResultSerializer(data={
            'action': 'download', 'parameters': {'dataset_id': 'wrong_value_type'}
        })
        with self.assertRaises(ValidationError) as assert_raises:
            self.assertFalse(serializer.is_valid(raise_exception=True))
        self.assertDictEqual(
            assert_raises.exception.detail,
            {'non_field_errors': [ErrorDetail(string='Invalid dataset_id', code='invalid')]}
        )

    def test_validate_error_on_wrong_parameter_value(self):
        """
        Validation must fail if a parameter value that is not in the valid choices
        is provided to an action
        """
        serializer = serializers.TaskResultSerializer(data={
            'action': 'convert', 'parameters': {'dataset_id': 1, 'format': 'wrong_value'}
        })
        with self.assertRaises(ValidationError) as assert_raises:
            self.assertFalse(serializer.is_valid(raise_exception=True))
        self.assertDictEqual(
            assert_raises.exception.detail,
            {'non_field_errors': [ErrorDetail(string='Invalid format', code='invalid')]}
        )

    def test_validate_error_on_wrong_number_of_parameters(self):
        """
        A ValidationError must be raised if the wrong number of parameters is provided to an action
        """
        serializer = serializers.TaskResultSerializer(data={
            'action': 'convert', 'parameters': {'dataset_id': 1}
        })
        with self.assertRaises(ValidationError) as assert_raises:
            self.assertFalse(serializer.is_valid(raise_exception=True))
        self.assertDictEqual(
            assert_raises.exception.detail,
            {
                'non_field_errors': [
                    ErrorDetail(
                        string="All the following parameters are required for action 'convert': ['dataset_id', 'format']",
                        code='invalid'
                    )
                ]
            }
        )

    def test_launch_download(self):
        """The download task must be called with the right parameters"""
        validated_data = {
            'action': 'download', 'parameters': {'dataset_id': 1}
        }
        serializer = serializers.TaskResultSerializer(data={})
        serializer.create(validated_data)
        self.tasks_mock.download.delay.assert_called_with(
            validated_data['parameters']['dataset_id'])

    def test_launch_idf_conversion(self):
        """The convert_to_idf task must be called with the right parameters"""
        validated_data = {
            'action': 'convert', 'parameters': {'dataset_id': 1, 'format': 'idf'}
        }
        serializer = serializers.TaskResultSerializer(data={})
        serializer.create(validated_data)
        self.tasks_mock.download.apply_async.assert_called_with(
            (validated_data['parameters']['dataset_id'],),
            link=self.tasks_mock.convert_to_idf.s.return_value
        )

    def test_task_representation(self):
        """The 'result' and 'meta' attributes of a task must be parsed and represented as a dict"""
        serializer = serializers.TaskResultSerializer()
        task_result = TaskResult.objects.get(pk=2)
        self.assertDictEqual(
            serializer.to_representation(task_result),
            {
                'task_id': 'df2bfb58-7d2e-4f83-9dc2-bac95a421c72',
                'task_name': 'geospaas_processing.tasks.download',
                'result': [1, 'ftp://test/dataset_1_S3A_OL_1_EFR____20181213T024322_20181213T024622_20181214T065355_0179_039_089_2340_LN1_O_NT_002.zip'],
                'status': 'SUCCESS',
                'task_args': '(1,)',
                'date_created': '2020-07-16T13:53:33.864000Z',
                'date_done': '2020-07-16T13:57:21.912000Z',
                'meta': {
                    'children': [[['733d3a63-7a5a-4a1e-8cf0-750ae393dd98', None], None]]
                }
            }
        )


    def test_update_does_nothing(self):
        """The update() method must do nothing"""
