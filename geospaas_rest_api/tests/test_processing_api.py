"""Tests for the long-running tasks endpoint of the GeoSPaaS REST API"""
import importlib
import os
import unittest
import unittest.mock as mock
from datetime import datetime

import celery
import celery.result
import django.db
import django.test
import geospaas_processing.tasks.core as tasks_core
import geospaas_processing.tasks.idf as tasks_idf
import geospaas_processing.tasks.syntool as tasks_syntool
from rest_framework.exceptions import ErrorDetail, ValidationError

import geospaas_rest_api.models as models
import geospaas_rest_api.processing_api.serializers as serializers


os.environ.setdefault('GEOSPAAS_REST_API_ENABLE_PROCESSING', 'true')


class TaskViewSetTests(django.test.TestCase):
    """Test tasks/ endpoints"""

    fixtures = ['processing_tests_data']

    def test_list_tasks(self):
        """The list of tasks must be returned"""
        expected_result = {
            'next': None, 'previous': None,
            'results': [
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
        }
        self.assertJSONEqual(self.client.get('/api/tasks/').content, expected_result)

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

    def test_abstract_check_parameters(self):
        """
        Any attempt to access the signature attribute on the
        `Job` class should raise a NotImplementedError
        """
        with self.assertRaises(NotImplementedError):
            models.Job.check_parameters({})

    def test_abstract_get_signature(self):
        """get_signature() should raise a NotImplementedError"""
        with self.assertRaises(NotImplementedError):
            models.Job.get_signature({})

    def test_abstract_make_task_parameters(self):
        """make_task_parameters() should raise a NotImplementedError"""
        with self.assertRaises(NotImplementedError):
            models.Job.make_task_parameters({})

    def test_run_job(self):
        """
        `Job.run()` must launch the celery tasks and
        return a job instance pointing to the first task
        """
        with mock.patch.object(models.Job, 'get_signature') as mock_get_signature, \
             mock.patch.object(models.Job, 'make_task_parameters') as mock_make_params:
            mock_get_signature.return_value.delay.return_value.task_id = 1
            mock_make_params.side_effect = lambda p: ([], p)
            job = models.Job.run({'foo': 'bar'})
        mock_get_signature.return_value.delay.assert_called_with(foo='bar')
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


class DownloadJobTests(unittest.TestCase):
    """Tests for the DownloadJob class"""

    def test_get_signature_no_cropping(self):
        """Test getting the right signature when no cropping is
        required
        """
        with mock.patch('geospaas_rest_api.processing_api.models.tasks_core') as mock_tasks, \
             mock.patch('celery.chain') as mock_chain:
            _ = models.DownloadJob.get_signature({})
        mock_chain.assert_called_with([
            mock_tasks.download.signature.return_value,
            mock_tasks.archive.signature.return_value,
            mock_tasks.publish.signature.return_value,
        ])

    def test_get_signature_cropping(self):
        """Test getting the right signature when cropping is required
        """
        with mock.patch('geospaas_rest_api.processing_api.models.tasks_core') as mock_tasks, \
             mock.patch('celery.chain') as mock_chain:
            _ = models.DownloadJob.get_signature({'bounding_box': [0, 20, 20, 0]})
        mock_chain.assert_called_with(
            [
                mock_tasks.download.signature.return_value,
                mock_tasks.unarchive.signature.return_value,
                mock_tasks.crop.signature.return_value,
                mock_tasks.archive.signature.return_value,
                mock_tasks.publish.signature.return_value,
            ])
        self.assertListEqual(
            mock_tasks.crop.signature.call_args[1]['kwargs']['bounding_box'],
            [0, 20, 20, 0])

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
                         code='invalid')])

    def test_check_parameters_extra_param(self):
        """`check_parameters()` must raise an exception if an extra parameter is given"""
        parameters = {'dataset_id': 1, 'extra_param': 'foo'}
        with self.assertRaises(ValidationError) as raised:
            models.DownloadJob.check_parameters(parameters)
        self.assertListEqual(
            raised.exception.detail,
            [ErrorDetail(string="The download action accepts only one parameter: 'dataset_id'",
                         code='invalid')])

    def test_check_parameters_wrong_id_type(self):
        """`check_parameters()` must raise an exception if the
        'dataset_id' value is of the wrong type
        """
        with self.assertRaises(ValidationError) as raised:
            models.DownloadJob.check_parameters({'dataset_id': '1'})
        self.assertListEqual(
            raised.exception.detail,
            [ErrorDetail(string="'dataset_id' must be an integer", code='invalid')])

    def test_check_parameters_wrong_bounding_box_type(self):
        """`check_parameters()` must raise an exception if the
        'bounding_box' value is of the wrong type or length
        """
        with self.assertRaises(ValidationError):
            models.DownloadJob.check_parameters({'dataset_id': 1, 'bounding_box': '2'})
        with self.assertRaises(ValidationError):
            models.DownloadJob.check_parameters({'dataset_id': 1, 'bounding_box': [2]})


class ConvertJobTests(unittest.TestCase):
    """Tests for the ConvertJob class"""

    def test_check_parameters_ok(self):
        """Test the checking of correct parameters"""
        parameters = {'dataset_id': 1, 'format': 'idf'}
        self.assertEqual(models.ConvertJob.check_parameters(parameters), parameters)

    def test_check_parameters_wrong_key(self):
        """`check_parameters()` must raise an exception if there is a wrong key in the parameters"""
        parameters = {'dataset_id': 1, 'format': 'idf', 'wrong_key': 1}
        with self.assertRaises(ValidationError) as raised:
            models.ConvertJob.check_parameters(parameters)
        self.assertListEqual(
            raised.exception.detail,
            [ErrorDetail(string="The convert action accepts only these parameters: "
                                "dataset_id, format, bounding_box, skip_check, converter_options",
                         code='invalid')])

    def test_check_parameters_wrong_format(self):
        """`check_parameters()` must raise an exception if the format
        is not one of the valid options
        """
        parameters = {'dataset_id': 1, 'format': 'foo',}
        with self.assertRaises(ValidationError) as raised:
            models.ConvertJob.check_parameters(parameters)

    def test_check_parameters_extra_param(self):
        """`check_parameters()` must raise an exception if an extra parameter is given"""
        parameters = {'dataset_id': 1, 'extra_param': 'foo'}
        with self.assertRaises(ValidationError) as raised:
            models.ConvertJob.check_parameters(parameters)
        self.assertListEqual(
            raised.exception.detail,
            [ErrorDetail(string="The convert action accepts only these parameters: "
                                "dataset_id, format, bounding_box, skip_check, converter_options",
                         code='invalid')])

    def test_check_parameters_wrong_type_for_dataset_id(self):
        """
        `check_parameters()` must raise an exception if
        the 'dataset_id' value is of the wrong type
        """
        parameters = {'dataset_id': '1'}
        with self.assertRaises(ValidationError) as raised:
            models.ConvertJob.check_parameters(parameters)
        self.assertListEqual(
            raised.exception.detail,
            [ErrorDetail(string="'dataset_id' must be an integer", code='invalid')])

    def test_check_parameters_wrong_bounding_box_type(self):
        """`check_parameters()` must raise an exception if the
        'bounding_box' value is of the wrong type or length
        """
        with self.assertRaises(ValidationError):
            models.ConvertJob.check_parameters(
                {'dataset_id': 1, 'format': 'idf', 'bounding_box': '2'})
        with self.assertRaises(ValidationError):
            models.ConvertJob.check_parameters(
                {'dataset_id': 1, 'format': 'idf', 'bounding_box': [2]})

    def test_check_parameters_wrong_converter_options_type(self):
        """`check_parameters()` must raise an exception if the
        'converter_options' value is of the wrong type
        """
        with self.assertRaises(ValidationError):
            models.ConvertJob.check_parameters(
                {'dataset_id': 1, 'format': 'idf', 'converter_options': '2'})

    def test_get_signature_syntool(self):
        """Test the right signature is returned"""
        self.maxDiff = None
        base_chain = celery.chain(
            tasks_core.download.signature(),
            tasks_core.unarchive.signature(),
            tasks_core.crop.signature(
                kwargs={'bounding_box': [0, 20, 20, 0]}),
            tasks_syntool.convert.signature(kwargs={'converter_options': None}),
            tasks_syntool.db_insert.signature(),
            tasks_core.remove_downloaded.signature())

        self.assertEqual(
            models.ConvertJob.get_signature({
                'format': 'syntool',
                'bounding_box': [0, 20, 20, 0]
            }),
            tasks_syntool.check_ingested.signature(kwargs={'to_execute': base_chain}))

        self.assertEqual(
            models.ConvertJob.get_signature({
                'format': 'syntool',
                'bounding_box': [0, 20, 20, 0],
                'skip_check': True
            }),
            base_chain)

    def test_get_signature_idf(self):
        """Test the right signature is returned"""
        self.assertEqual(
            models.ConvertJob.get_signature({
                'format': 'idf',
                'bounding_box': [0, 20, 20, 0]
            }),
            celery.chain(
                tasks_core.download.signature(),
                tasks_core.unarchive.signature(),
                tasks_core.crop.signature(
                    kwargs={'bounding_box': [0, 20, 20, 0]}),
                tasks_idf.convert_to_idf.signature(),
                tasks_core.archive.signature(),
                tasks_core.publish.signature())
        )

    def test_get_signature_wrong_format(self):
        """An exception should be raised when trying to get a signature
        using an invalid format. This should never happen since
        parameters are checked before
        """
        with self.assertRaises(RuntimeError):
            _ = models.ConvertJob.get_signature({'format': 'foo'})


class SyntoolCleanupJobTests(unittest.TestCase):
    """Tests for the SyntoolCleanupJob class"""

    def test_get_signature(self):
        """Test getting the right signature"""
        with mock.patch(
                'geospaas_rest_api.processing_api.models.tasks_syntool') as mock_syntool_tasks:
            self.assertEqual(
                models.SyntoolCleanupJob.get_signature({}),
                mock_syntool_tasks.cleanup.signature.return_value)

    def test_check_parameters_ok(self):
        """Test that check_parameters() returns the parameters when
        they are valid
        """
        self.assertDictEqual(
            models.SyntoolCleanupJob.check_parameters({'criteria': {'id': 539}}),
            {'criteria': {'id': 539}})

    def test_check_parameters_unknown(self):
        """An error should be raised when an unknown parameter is given
        """
        with self.assertRaises(ValidationError):
            models.SyntoolCleanupJob.check_parameters({'foo': 'bar'})

    def test_check_parameters_no_criteria(self):
        """An error should be raised when the criteria parameter is
        absent
        """
        with self.assertRaises(ValidationError):
            models.SyntoolCleanupJob.check_parameters({})

    def test_check_parameters_wrong_type(self):
        """An error should be raised when `criteria` is not a dictionary
        """
        with self.assertRaises(ValidationError):
            models.SyntoolCleanupJob.check_parameters({'criteria': 'id=1'})

    def test_make_task_parameters(self):
        """Test that the right arguments are builts from the request
        parameters
        """
        self.assertTupleEqual(
            models.SyntoolCleanupJob.make_task_parameters({'criteria': {'id': 539}}),
            (({'id': 539},), {}))


class HarvestJobTests(unittest.TestCase):
    """Tests for the HarvestJob class"""

    def test_get_signature(self):
        """Test getting the right signature"""
        with mock.patch(
            'geospaas_rest_api.processing_api.models.tasks_harvesting') as mock_harvesting_tasks:
            self.assertEqual(
                models.HarvestJob.get_signature({}),
                mock_harvesting_tasks.start_harvest.signature.return_value)

    def test_check_parameters_ok(self):
        """Test that check_parameters() returns the parameters when
        they are valid"""
        self.assertDictEqual(
            models.HarvestJob.check_parameters({'search_config_dict': {}}),
            {'search_config_dict': {}})

    def test_check_parameters_unknown(self):
        """An error should be raised when an unknown parameter is given
        """
        with self.assertRaises(ValidationError):
            models.HarvestJob.check_parameters({'foo': 'bar'})

    def test_check_parameters_wrong_type(self):
        """An error should be raised when `search_config_dict` is not a
        dict
        """
        with self.assertRaises(ValidationError):
            models.HarvestJob.check_parameters({'search_config_dict': 'foo'})

    def test_make_task_parameters(self):
        """Test that the right arguments are builts from the request
        parameters
        """
        self.assertTupleEqual(
            models.HarvestJob.make_task_parameters({'search_config_dict': {'foo': 'bar'}}),
            (({'foo': 'bar'},), {}))


class JobViewSetTests(django.test.TestCase):
    """Test jobs/ endpoints"""

    fixtures = ['processing_tests_data']

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
        expected_result = {
            'next': None, 'previous': None,
            'results': [
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
        }
        with mock.patch.object(models.Job, 'get_current_task_result') as mock_get_result:
            mock_result = mock.Mock(spec=celery.result.AsyncResult)
            mock_result.state = 'PLACEHOLDER'
            mock_get_result.return_value = (mock_result, False)
            self.assertJSONEqual(self.client.get('/api/jobs/').content, expected_result)

    def test_get_unfinished_job(self):
        """Test that a single unfinished job can be retrieved"""
        expected_job = {
            "id": 1,
            "task_id": "df2bfb58-7d2e-4f83-9dc2-bac95a421c72",
            "status": 'PLACEHOLDER',
            "date_created": '2020-07-16T13:53:30Z',
        }
        with mock.patch.object(models.Job, 'get_current_task_result') as mock_get_result:
            mock_result = mock.Mock(spec=celery.result.AsyncResult)
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
            mock_result = mock.Mock(spec=celery.result.AsyncResult)
            mock_result.state = 'SUCCESS'
            mock_result.result = [1, 'foo']
            mock_result.date_done = 'bar'
            mock_get_result.return_value = (mock_result, True)
            response = self.client.get('/api/jobs/1/')
            self.assertJSONEqual(response.content, expected_job)


class JobSerializerTests(django.test.TestCase):
    """Tests for the JobSerializer"""

    fixtures = ['processing_tests_data']

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
        with mock.patch.object(models.DownloadJob, 'get_signature') as mock_get_signature, \
             mock.patch('geospaas_rest_api.models.isinstance', return_value=True):
            mock_get_signature.return_value.delay.return_value.task_id = 1
            serializer.create(validated_data)
            mock_get_signature.return_value.delay.assert_called_with(
                (validated_data['parameters']['dataset_id'],))

    def test_launch_idf_conversion(self):
        """The convert_to_idf task must be called with the right parameters"""
        validated_data = {
            'action': 'convert', 'parameters': {'dataset_id': 1, 'format': 'idf'}
        }
        serializer = serializers.JobSerializer()
        with mock.patch.object(models.ConvertJob, 'get_signature') as mock_get_signature, \
             mock.patch('geospaas_rest_api.models.isinstance', return_value=True):
            mock_get_signature.return_value.delay.return_value.task_id = 1
            serializer.create(validated_data)
            mock_get_signature.return_value.delay.assert_called_with(
                (validated_data['parameters']['dataset_id'],))

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
            mock_result = mock.Mock(spec=celery.result.AsyncResult)
            mock_result.state = 'PLACEHOLDER'
            mock_get_result.return_value = (mock_result, False)
            self.assertDictEqual(
                serializers.JobSerializer().to_representation(models.Job.objects.get(id=1)),
                {
                    "id": 1,
                    "task_id": "df2bfb58-7d2e-4f83-9dc2-bac95a421c72",
                    "status": 'PLACEHOLDER',
                    "date_created": '2020-07-16T13:53:30Z',
                })

    def test_unfinished_job_parallel_tasks_representation(self):
        """The representation of a job which has not finished executing
        and is running several tasks in parallel should have the state
        of each task in its status property.
        """
        with mock.patch.object(models.Job, 'get_current_task_result') as mock_get_result:
            mock_result = mock.MagicMock(spec=celery.result.ResultSet)
            mock_result.__iter__.return_value = [mock.Mock(task_id='foo', state='PLACEHOLDER1'),
                                                 mock.Mock(task_id='bar', state='PLACEHOLDER2')]
            mock_get_result.return_value = (mock_result, False)
            self.assertDictEqual(
                serializers.JobSerializer().to_representation(models.Job.objects.get(id=1)),
                {
                    "id": 1,
                    "task_id": "df2bfb58-7d2e-4f83-9dc2-bac95a421c72",
                    "status": {
                        'foo': 'PLACEHOLDER1',
                        'bar': 'PLACEHOLDER2',
                    },
                    "date_created": '2020-07-16T13:53:30Z',
                })

    def test_finished_job_representation(self):
        """
        The representation of a job which has finished executing
        should have the following fields:
          - id
          - task_id
          - status
          - date_created
          - date_done
          - result
        """
        expected_base_dict = {
            "id": 1,
            "task_id": "df2bfb58-7d2e-4f83-9dc2-bac95a421c72",
            "status": 'PLACEHOLDER',
            "date_created": '2020-07-16T13:53:30Z',
            "date_done": 'PLACEHOLDER'
        }
        with mock.patch.object(models.Job, 'get_current_task_result') as mock_get_result:
            mock_result = mock.Mock(spec=celery.result.AsyncResult)
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
                {**expected_base_dict, 'result': 'PLACEHOLDER'})

            mock_result.state = 'FAILURE'
            mock_result.traceback = 'error happened'
            expected_base_dict['status'] = 'FAILURE'
            self.assertDictEqual(
                serializers.JobSerializer().to_representation(models.Job.objects.get(id=1)),
                {**expected_base_dict, 'result': 'error happened'})

    def test_choose_job_class(self):
        """Test getting the right class based on the action parameter
        """
        serializer = serializers.JobSerializer()
        self.assertEqual(
            serializer.choose_job_class({'action': 'download', 'parameters': {}}),
            models.DownloadJob)
        self.assertEqual(
            serializer.choose_job_class({'action': 'convert', 'parameters': {'format': 'idf'}}),
            models.ConvertJob)
        self.assertEqual(
            serializer.choose_job_class({'action': 'convert', 'parameters': {'format': 'syntool'}}),
            models.ConvertJob)
        self.assertEqual(
            serializer.choose_job_class({'action': 'harvest', 'parameters': {}}),
            models.HarvestJob)
        self.assertEqual(
            serializer.choose_job_class({'action': 'syntool_cleanup'}),
            models.SyntoolCleanupJob)


class ProcessingResultsViewSetTests(django.test.TestCase):
    """Test processing_results/ endpoints"""

    fixtures = ['processing_tests_data']

    def test_list_tasks(self):
        """The list of processing results must be returned"""
        expected_result = {
            'next': None, 'previous': None,
            'results': [
                {
                    "id": 1,
                    "dataset": 1,
                    "path": "ingested/product_name/granule_name_1/",
                    "type": "syntool",
                    "created": "2023-10-25T15:38:47Z"
                }, {
                    "id": 2,
                    "dataset": 2,
                    "path": "ingested/product_name/granule_name_2/",
                    "type": "syntool",
                    "created": "2023-10-26T09:10:19Z"
                }
            ]
        }
        self.assertJSONEqual(self.client.get('/api/processing_results/').content, expected_result)

    def test_retrieve_task(self):
        """The representation of the processing result must be returned"""
        response = self.client.get('/api/processing_results/1/')
        self.assertJSONEqual(response.content, {
            "id": 1,
            "dataset": 1,
            "path": "ingested/product_name/granule_name_1/",
            "type": "syntool",
            "created": "2023-10-25T15:38:47Z"
        })
