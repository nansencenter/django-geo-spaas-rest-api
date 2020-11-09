"""Tests for the long-running tasks endpoint of the GeoSPaaS REST API"""
import os
import unittest
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
        mock.patch('geospaas_rest_api.models.tasks').start()
        self.addCleanup(mock.patch.stopall)

    def test_error_on_check_parameters_execution(self):
        """
        Any attempt to access the signature attribute on the
        `Job` class should raise a NotImplementedError
        """
        with self.assertRaises(NotImplementedError):
            models.Job.check_parameters(None)

    def test_run_job(self):
        """
        `Job.run()` must launch the celery tasks and
        return a job instance pointing to the first task
        """
        with mock.patch.object(models.Job, 'signature') as mock_signature:
            mock_signature.delay.return_value.task_id = 1
            job = models.Job.run('foo')
        mock_signature.delay.assert_called_with('foo')
        self.assertIsInstance(job, models.Job)

    def test_run_job_error_if_tasks_not_importable(self):
        """`Job.run()` must raise an exception if `geospaas_processing.tasks` is not importable"""
        with mock.patch('geospaas_rest_api.models.tasks', None):
            with mock.patch.object(models.Job, 'signature'):
                with self.assertRaises(ImportError):
                    models.Job.run()

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


class DownloadJobTests(unittest.TestCase):
    """Tests for the DownloadJob class"""

    def test_check_parameters_ok(self):
        """Test the checking of correct parameters"""
        parameters = {'dataset_id': 1}
        self.assertEqual(models.DownloadJob.check_parameters(parameters), parameters)

    def test_check_parameters_wrong_key(self):
        """`check_parameters()` must raise an exception if there is a wrong key in the parameters"""
        parameters = {'wrong_key': 1}
        with self.assertRaises(ValidationError) as raised:
            models.DownloadJob.check_parameters(parameters)
        self.assertListEqual(
            raised.exception.detail,
            [ErrorDetail(string="The download action accepts only one parameter: 'dataset_id'",
                         code='invalid')]
        )

    def test_check_parameters_extra_param(self):
        """`check_parameters()` must raise an exception if an extra parameter is given"""
        parameters = {'dataset_id': 1, 'extra_param': 'foo'}
        with self.assertRaises(ValidationError) as raised:
            models.DownloadJob.check_parameters(parameters)
        self.assertListEqual(
            raised.exception.detail,
            [ErrorDetail(string="The download action accepts only one parameter: 'dataset_id'",
                         code='invalid')]
        )

    def test_check_parameters_wrong_type(self):
        """
        `check_parameters()` must raise an exception if
        the 'dataset_id' value is of the wrong type
        """
        parameters = {'dataset_id': '1'}
        with self.assertRaises(ValidationError) as raised:
            models.DownloadJob.check_parameters(parameters)
        self.assertListEqual(
            raised.exception.detail,
            [ErrorDetail(string="'dataset_id' must be an integer", code='invalid')]
        )


class ConvertJob(unittest.TestCase):
    """Tests for the ConvertJob class"""

    def test_check_parameters_ok(self):
        """Test the checking of correct parameters"""
        parameters = {'dataset_id': 1, 'format': 'idf'}
        self.assertEqual(models.ConvertJob.check_parameters(parameters), parameters)

    def test_check_parameters_wrong_key(self):
        """`check_parameters()` must raise an exception if there is a wrong key in the parameters"""
        parameters = {'wrong_key': 1, 'format': 'idf'}
        with self.assertRaises(ValidationError) as raised:
            models.ConvertJob.check_parameters(parameters)
        self.assertListEqual(
            raised.exception.detail,
            [ErrorDetail(
                string="The download action accepts only these parameter: dataset_id, format",
                code='invalid')]
        )

    def test_check_parameters_extra_param(self):
        """`check_parameters()` must raise an exception if an extra parameter is given"""
        parameters = {'dataset_id': 1, 'format': 'idf', 'extra_param': 'foo'}
        with self.assertRaises(ValidationError) as raised:
            models.ConvertJob.check_parameters(parameters)
        self.assertListEqual(
            raised.exception.detail,
            [ErrorDetail(
                string="The download action accepts only these parameter: dataset_id, format",
                code='invalid')]
        )

    def test_check_parameters_wrong_type_for_dataset_id(self):
        """
        `check_parameters()` must raise an exception if
        the 'dataset_id' value is of the wrong type
        """
        parameters = {'dataset_id': '1', 'format': 'idf'}
        with self.assertRaises(ValidationError) as raised:
            models.ConvertJob.check_parameters(parameters)
        self.assertListEqual(
            raised.exception.detail,
            [ErrorDetail(string="'dataset_id' must be an integer", code='invalid')]
        )

    def test_check_parameters_wrong_value_for_format(self):
        """
        `check_parameters()` must raise an exception if
        the 'dataset_id' value is of the wrong type
        """
        parameters = {'dataset_id': 1, 'format': 'nc'}
        with self.assertRaises(ValidationError) as raised:
            models.ConvertJob.check_parameters(parameters)
        self.assertListEqual(
            raised.exception.detail,
            [ErrorDetail(string="'format' only accepts the following values: idf", code='invalid')]
        )


class JobViewSetTests(django.test.TestCase):
    """Test jobs/ endpoints"""

    fixtures = ['processing_tests_data']

    def setUp(self):
        # This mock is necessary to avoid disabling the TaskViewSet when tests are run in an
        # environment where geospaas_processing is not installed.
        mock.patch('geospaas_rest_api.models.tasks').start()
        self.addCleanup(mock.patch.stopall)

    def test_jobs_inaccessible_if_geospaas_processing_not_importable(self):
        """
        If geospaas_processing is not importable, the 'jobs/' endpoint should not be accessible
        """
        with mock.patch('geospaas_rest_api.models.tasks', None):
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

    def test_get_unfinished_job(self):
        """Test that a single unfinished job can be retrieved"""
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

    def test_get_successful_job(self):
        """Test that a successful job can be retrieved"""
        expected_job = {
            "id": 1,
            "task_id": "df2bfb58-7d2e-4f83-9dc2-bac95a421c72",
            "status": 'SUCCESS',
            "result": [1, 'foo'],
            "date_created": '2020-07-16T13:53:30Z',
            "date_done": 'bar'
        }
        with mock.patch.object(models.Job, 'get_current_task_result') as mock_get_result:
            mock_result = mock.Mock()
            mock_result.state = 'SUCCESS'
            mock_result.result = [1, 'foo']
            mock_result.date_done = 'bar'
            mock_get_result.return_value = (mock_result, True)
            response = self.client.get('/api/jobs/1/')
            self.assertJSONEqual(response.content, expected_job)


class JobSerializerTests(django.test.TestCase):
    """Tests for the JobSerializer"""

    fixtures = ['processing_tests_data']

    def setUp(self):
        tasks_patcher = mock.patch('geospaas_rest_api.models.tasks')
        self.tasks_mock = tasks_patcher.start()
        self.addCleanup(mock.patch.stopall)

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

    def test_launch_download(self):
        """The download task must be called with the right parameters"""
        validated_data = {
            'action': 'download', 'parameters': {'dataset_id': 1}
        }
        serializer = serializers.JobSerializer()
        with mock.patch.object(models.DownloadJob, 'signature') as mock_signature:
            mock_signature.delay.return_value.task_id = 1
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
        with mock.patch.object(models.ConvertJob, 'signature') as mock_signature:
            mock_signature.delay.return_value.task_id = 1
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

    def test_finished_job_representation_no_success(self):
        """
        The representation of a job which has finished executing
        should have the following fields:
          - id
          - task_id
          - status
          - date_created
          - date_done
          - result if the status is success
        """
        expected_base_dict = {
            "id": 1,
            "task_id": "df2bfb58-7d2e-4f83-9dc2-bac95a421c72",
            "status": 'PLACEHOLDER',
            "date_created": '2020-07-16T13:53:30Z',
            "date_done": 'PLACEHOLDER'
        }
        with mock.patch.object(models.Job, 'get_current_task_result') as mock_get_result:
            mock_result = mock.Mock()
            mock_result.state = 'PLACEHOLDER'
            mock_result.date_done = 'PLACEHOLDER'
            mock_result.result = 'PLACEHOLDER'
            mock_get_result.return_value = (mock_result, True)
            self.assertDictEqual(
                serializers.JobSerializer().to_representation(models.Job.objects.get(id=1)),
                expected_base_dict
            )

            mock_result.state = 'SUCCESS'
            expected_base_dict['status'] = 'SUCCESS'
            self.assertDictEqual(
                serializers.JobSerializer().to_representation(models.Job.objects.get(id=1)),
                {**expected_base_dict, 'result': 'PLACEHOLDER'}
            )
