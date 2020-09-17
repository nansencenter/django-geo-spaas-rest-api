"""Tests for the long-running tasks endpoint of the GeoSPaaS REST API"""
import os
import unittest.mock as mock

import celery
import celery.result
import django.db
import django.test
from rest_framework.exceptions import ErrorDetail, ValidationError

import geospaas_rest_api.models as models
import geospaas_rest_api.serializers as serializers


os.environ.setdefault('GEOSPAAS_REST_API_ENABLE_PROCESSING', 'true')


class TaskViewSetTests(django.test.TestCase):
    """Test tasks/ endpoints"""

    fixtures = ['processing_tests_data']

    def test_list_tasks(self):
        """The list of tasks must be returned"""
        expected_tasks = [
            {
                'id': 4,
                'content_encoding': 'utf-8',
                'content_type': 'application/json',
                'worker': 'celery@3b6b6202fcbe',
                'traceback': None,
                'task_kwargs': '{}',
                'task_id': '733d3a63-7a5a-4a1e-8cf0-750ae393dd99',
                'task_name': 'geospaas_processing.tasks.convert_to_idf',
                'result': "[1, \"ftp://test/sentinel3_olci_l1_efr/S3A_OL_1_EFR____20181213T024322_20181213T024622_20181214T065355_0179_039_089_2340_LN1_O_NT_002.SEN3\"]",
                'status': 'SUCCESS',
                'task_args': "((1, 'ftp://test/dataset_1_S3A_OL_1_EFR____20181213T024322_20181213T024622_20181214T065355_0179_039_089_2340_LN1_O_NT_002.zip'),)",
                'date_created': '2020-07-16T13:58:22.918000Z',
                'date_done': '2020-07-16T13:58:21.201000Z',
                'meta': "{\"children\": []}"
            }, {
                'id': 3,
                'content_encoding': 'utf-8',
                'content_type': 'application/json',
                'worker': 'celery@3b6b6202fcbe',
                'traceback': None,
                'task_kwargs': '{}',
                'task_id': '733d3a63-7a5a-4a1e-8cf0-750ae393dd98',
                'task_name': 'geospaas_processing.tasks.convert_to_idf',
                'result': "{\"pid\": 23, \"hostname\": \"celery@3b6b6202fcbe\"}",
                'status': 'STARTED',
                'task_args': "((1, 'ftp://test/dataset_1_S3A_OL_1_EFR____20181213T024322_20181213T024622_20181214T065355_0179_039_089_2340_LN1_O_NT_002.zip'),)",
                'date_created': '2020-07-16T13:57:21.918000Z',
                'date_done': '2020-07-16T13:57:21.918000Z',
                'meta': "{\"children\": []}"
            }, {
                'id': 2,
                'content_encoding': 'utf-8',
                'content_type': 'application/json',
                'worker': 'celery@3b6b6202fcbe',
                'traceback': None,
                'task_kwargs': '{}',
                'task_id': 'df2bfb58-7d2e-4f83-9dc2-bac95a421c72',
                'task_name': 'geospaas_processing.tasks.download',
                'result': "[1, \"ftp://test/dataset_1_S3A_OL_1_EFR____20181213T024322_20181213T024622_20181214T065355_0179_039_089_2340_LN1_O_NT_002.zip\"]",
                'status': 'SUCCESS',
                'task_args': '(1,)',
                'date_created': '2020-07-16T13:53:33.864000Z',
                'date_done': '2020-07-16T13:57:21.912000Z',
                'meta': "{\"children\": [[[\"733d3a63-7a5a-4a1e-8cf0-750ae393dd98\", null], null]]}"
            }, {
                'id': 1,
                'content_encoding': 'utf-8',
                'content_type': 'application/json',
                'worker': 'celery@3b6b6202fcbe',
                'traceback': None,
                'task_kwargs': '{}',
                'task_id': 'df2bfb58-7d2e-4f83-9dc2-bac95a421c71',
                'task_name': 'geospaas_processing.tasks.download',
                'result': "{\"pid\": 22, \"hostname\": \"celery@3b6b6202fcbe\"}",
                'status': 'STARTED',
                'task_args': '(1,)',
                'date_created': '2020-07-16T13:52:33.864000Z',
                'date_done': '2020-07-16T13:52:33.864000Z',
                'meta': "{\"children\": []}"
            }
        ]
        self.assertJSONEqual(self.client.get('/api/tasks/').content, expected_tasks)

    def test_retrieve_task(self):
        """The representation of the task must be returned"""
        response = self.client.get('/api/tasks/df2bfb58-7d2e-4f83-9dc2-bac95a421c71/')
        self.assertJSONEqual(response.content, {
            "id": 1,
            "task_id": "df2bfb58-7d2e-4f83-9dc2-bac95a421c71",
            "task_name": "geospaas_processing.tasks.download",
            "task_args": "(1,)",
            "task_kwargs": "{}",
            "status": "STARTED",
            "worker": "celery@3b6b6202fcbe",
            "content_type": "application/json",
            "content_encoding": "utf-8",
            "result": "{\"pid\": 22, \"hostname\": \"celery@3b6b6202fcbe\"}",
            "date_created": "2020-07-16T13:52:33.864000Z",
            "date_done": "2020-07-16T13:52:33.864000Z",
            "traceback": None,
            "meta": "{\"children\": []}"
        })


class JobModelTests(django.test.TestCase):
    """Tests for the Job model"""

    fixtures = ['processing_tests_data']

    def setUp(self):
        # This mock is necessary to avoid disabling the TaskViewSet when tests are run in an
        # environment where geospaas_processing is not installed.
        mock.patch('geospaas_rest_api.serializers.tasks').start()
        self.addCleanup(mock.patch.stopall)

    def test_run_job(self):
        """
        `Job.run()` must launch the celery tasks and
        return a job instance pointing to the first task
        """
        mock_signature = mock.Mock()
        mock_signature.delay.return_value.task_id = 1
        job = models.Job.run(mock_signature, 'foo')
        mock_signature.delay.assert_called_with('foo')
        self.assertIsInstance(job, models.Job)

    def test_get_current_task_result(self):
        """
        `get_current_task_result()` must return an AsyncResult object associated with the task
        currently executing, or the last task if all have finished
        """
        app = celery.Celery('geospaas_processing')
        app.config_from_object('django.conf:settings', namespace='CELERY')

        # Running job
        job = models.Job.objects.get(id=1)
        expected_result = celery.result.AsyncResult('733d3a63-7a5a-4a1e-8cf0-750ae393dd98')
        self.assertEqual(
            job.get_current_task_result(),
            (expected_result, False)
        )

        # Finished job
        job = models.Job.objects.get(id=2)
        expected_result = celery.result.AsyncResult('733d3a63-7a5a-4a1e-8cf0-750ae393dd99')
        self.assertEqual(
            job.get_current_task_result(),
            (expected_result, True)
        )

    def test_validate_error_on_wrong_parameter_key(self):
        """Validation must fail if wrong parameter keys are provided to an action"""
        parameters = {'wrong_key': 1}
        valid_parameters = serializers.JobSerializer.jobs['download']['valid_parameters']
        with self.assertRaises(ValidationError) as assert_raises:
            self.assertFalse(models.Job.validate_parameters(valid_parameters, parameters))
        self.assertListEqual(
            assert_raises.exception.detail,
            [ErrorDetail(string="Invalid parameter 'wrong_key'", code='invalid')]
        )

    def test_validate_error_on_wrong_parameter_value_type(self):
        """Validation must fail if the wrong type of parameter value is provided to an action"""
        parameters = {'dataset_id': 'wrong_value_type'}
        valid_parameters = serializers.JobSerializer.jobs['download']['valid_parameters']
        with self.assertRaises(ValidationError) as assert_raises:
            self.assertFalse(models.Job.validate_parameters(valid_parameters, parameters))
        self.assertListEqual(
            assert_raises.exception.detail,
            [ErrorDetail(string="Invalid value for 'dataset_id'", code='invalid')]
        )

    def test_validate_error_on_wrong_parameter_value(self):
        """
        Validation must fail if a parameter value that is not in the valid choices
        is provided to an action
        """
        parameters = {'dataset_id': 1, 'format': 'wrong_value'}
        valid_parameters = serializers.JobSerializer.jobs['convert']['valid_parameters']
        with self.assertRaises(ValidationError) as assert_raises:
            self.assertFalse(models.Job.validate_parameters(valid_parameters, parameters))
        self.assertListEqual(
            assert_raises.exception.detail,
            [ErrorDetail(string="Invalid value for 'format'", code='invalid')]
        )

    def test_validate_error_on_wrong_number_of_parameters(self):
        """
        A ValidationError must be raised if the wrong number of parameters is provided to an action
        """
        parameters = {'dataset_id': 1}
        valid_parameters = serializers.JobSerializer.jobs['convert']['valid_parameters']
        with self.assertRaises(ValidationError) as assert_raises:
            self.assertFalse(models.Job.validate_parameters(valid_parameters, parameters))
        self.assertListEqual(
            assert_raises.exception.detail,
            [ErrorDetail(
                string="All the following parameters are required: ['dataset_id', 'format']",
                code='invalid')]
        )


class JobViewSetTests(django.test.TestCase):
    """Test jobs/ endpoints"""

    fixtures = ['processing_tests_data']

    def setUp(self):
        # This mock is necessary to avoid disabling the TaskViewSet when tests are run in an
        # environment where geospaas_processing is not installed.
        mock.patch('geospaas_rest_api.serializers.tasks').start()
        self.addCleanup(mock.patch.stopall)

    def test_jobs_inaccessible_if_geospaas_processing_not_importable(self):
        """
        If geospaas_processing is not importable, the 'jobs/' endpoint should not be accessible
        """
        with mock.patch('geospaas_rest_api.serializers.tasks', None):
            self.assertEqual(self.client.get('/api/jobs/').status_code, 404)
            self.assertEqual(self.client.post('/api/jobs/', {}).status_code, 404)
            self.assertEqual(self.client.get('/api/jobs/1234').status_code, 404)

    def test_launch_job_if_valid_request_data(self):
        """A task must only be launched if the request data was successfully validated"""
        request_data = {'action': 'download', 'parameters': {'dataset_id': 1}}
        with mock.patch.object(serializers.JobSerializer, 'save') as save_mock:
            with mock.patch.object(serializers.JobSerializer, 'to_representation'):
                save_mock.return_value.id = '1234'
                self.client.post('/api/jobs/', request_data, 'application/json')
                save_mock.assert_called()

    def test_error_on_invalid_request_data(self):
        """
        A task must not be launched if the request data is invalid,
        and a 400 status code must be returned to the client
        """
        with mock.patch.object(serializers.JobSerializer, 'save') as save_mock:
            save_mock.return_value.id = '1234'
            response = self.client.post('/api/jobs/', {})
        save_mock.assert_not_called()
        self.assertEqual(400, response.status_code)

    def test_list_jobs(self):
        """Test that the list of tasks can be retrieved"""
        expected_jobs = [
            {
                "id": 2,
                "task_id": "733d3a63-7a5a-4a1e-8cf0-750ae393dd99",
                "status": 'PLACEHOLDER',
                "date_created": '2020-07-16T13:58:01.918000Z',
            },
            {
                "id": 1,
                "task_id": "df2bfb58-7d2e-4f83-9dc2-bac95a421c72",
                "status": 'PLACEHOLDER',
                "date_created": '2020-07-16T13:53:30Z',
            }
        ]
        with mock.patch.object(models.Job, 'get_current_task_result') as mock_get_result:
            mock_result = mock.Mock()
            mock_result.state = 'PLACEHOLDER'
            mock_get_result.return_value = (mock_result, False)
            self.assertJSONEqual(self.client.get('/api/jobs/').content, expected_jobs)

    def test_get_job(self):
        """Test that a single task can be retrieved"""
        expected_job = {
            "id": 1,
            "task_id": "df2bfb58-7d2e-4f83-9dc2-bac95a421c72",
            "status": 'PLACEHOLDER',
            "date_created": '2020-07-16T13:53:30Z',
        }
        with mock.patch.object(models.Job, 'get_current_task_result') as mock_get_result:
            mock_result = mock.Mock()
            mock_result.state = 'PLACEHOLDER'
            mock_get_result.return_value = (mock_result, False)
            response = self.client.get('/api/jobs/1/')
            self.assertJSONEqual(response.content, expected_job)


class JobSerializerTests(django.test.TestCase):
    """Tests for the JobSerializer"""

    fixtures = ['processing_tests_data']

    def setUp(self):
        tasks_patcher = mock.patch.object(serializers, 'tasks')
        self.tasks_mock = tasks_patcher.start()
        self.addCleanup(mock.patch.stopall)

    def test_error_if_geospaas_processing_not_importable(self):
        """
        It should not be possible to instantiate a JobSerializer
        if geospaas_processing.tasks is not importable
        """
        with mock.patch('geospaas_rest_api.serializers.tasks', None):
            with self.assertRaises(ImportError):
                serializers.JobSerializer()

    def test_validation_return_value(self):
        """Test tha the validate() method returns the validated data"""
        request_data = {'action': 'download', 'parameters': {'dataset_id': 1}}
        serializer = serializers.JobSerializer()
        self.assertDictEqual(serializer.validate(request_data), request_data)

    def test_validation_empty_data(self):
        """Validation must fail if the data is an empty dict"""
        serializer = serializers.JobSerializer(data={})
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
        serializer = serializers.JobSerializer(data={'parameters': {}})
        with self.assertRaises(ValidationError) as assert_raises:
            self.assertFalse(serializer.is_valid(raise_exception=True))
        self.assertDictEqual(
            assert_raises.exception.detail,
            {'action': [ErrorDetail(string='This field is required.', code='required')]}
        )

    def test_validation_no_parameter_field(self):
        """Validation must fail if the parameter field is not present"""
        serializer = serializers.JobSerializer(data={'action': 'download'})
        with self.assertRaises(ValidationError) as assert_raises:
            self.assertFalse(serializer.is_valid(raise_exception=True))
        self.assertDictEqual(
            assert_raises.exception.detail,
            {'parameters': [ErrorDetail(string='This field is required.', code='required')]}
        )

    def test_validation_parameter_field_not_dict(self):
        """Validation must fail if the parameter field is not a dictionary"""
        serializer = serializers.JobSerializer(data={'action': 'download', 'parameters': ''})
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
        serializer = serializers.JobSerializer(data={
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

    def test_launch_download(self):
        """The download task must be called with the right parameters"""
        validated_data = {
            'action': 'download', 'parameters': {'dataset_id': 1}
        }
        serializer = serializers.JobSerializer()
        mock_signature = mock.Mock()
        mock_jobs = {'download': {'signature': mock_signature}}
        mock_signature.delay.return_value.task_id = 1
        with mock.patch.object(serializers.JobSerializer, 'jobs', mock_jobs):
            serializer.create(validated_data)
            mock_signature.delay.assert_called_with(
                (validated_data['parameters']['dataset_id'],)
            )

    def test_launch_idf_conversion(self):
        """The convert_to_idf task must be called with the right parameters"""
        validated_data = {
            'action': 'convert', 'parameters': {'dataset_id': 1, 'format': 'idf'}
        }
        serializer = serializers.JobSerializer()
        mock_signature = mock.Mock()
        mock_jobs = {'convert': {'signature': mock_signature}}
        mock_signature.delay.return_value.task_id = 1
        with mock.patch.object(serializers.JobSerializer, 'jobs', mock_jobs):
            serializer.create(validated_data)
            mock_signature.delay.assert_called_with((validated_data['parameters']['dataset_id'],))

    def test_unfinished_job_representation(self):
        """
        The representation of a job which has not finished executing
        should have the following fields:
          - id
          - task_id
          - status
          - date_created
        """
        with mock.patch.object(models.Job, 'get_current_task_result') as mock_get_result:
            mock_result = mock.Mock()
            mock_result.state = 'PLACEHOLDER'
            mock_get_result.return_value = (mock_result, False)
            self.assertDictEqual(
                serializers.JobSerializer().to_representation(models.Job.objects.get(id=1)),
                {
                    "id": 1,
                    "task_id": "df2bfb58-7d2e-4f83-9dc2-bac95a421c72",
                    "status": 'PLACEHOLDER',
                    "date_created": '2020-07-16T13:53:30Z',
                }
            )

    def test_finished_job_representation(self):
        """
        The representation of a job which has not finished executing
        should have the following fields:
          - id
          - task_id
          - status
          - date_created
          - date_done
          - result
        """
        with mock.patch.object(models.Job, 'get_current_task_result') as mock_get_result:
            mock_result = mock.Mock()
            mock_result.state = 'PLACEHOLDER'
            mock_result.date_done = 'PLACEHOLDER'
            mock_result.result = 'PLACEHOLDER'
            mock_get_result.return_value = (mock_result, True)
            self.assertDictEqual(
                serializers.JobSerializer().to_representation(models.Job.objects.get(id=1)),
                {
                    "id": 1,
                    "task_id": "df2bfb58-7d2e-4f83-9dc2-bac95a421c72",
                    "status": 'PLACEHOLDER',
                    "date_created": '2020-07-16T13:53:30Z',
                    "date_done": 'PLACEHOLDER',
                    "result": 'PLACEHOLDER'
                }
            )
