"""Models for the GeoSPaaS REST API"""
from collections.abc import Sequence
try:
    import geospaas_processing.tasks as tasks
except ImportError:
    tasks = None

from celery.result import AsyncResult
from django.db import models
from rest_framework.exceptions import ValidationError


class Job(models.Model):
    """
    Intermediate model that gives access to the status and result of a series of linked Celery tasks
    """
    # Database fields
    task_id = models.CharField(
        unique=True, max_length=255,
        help_text='ID of the first task in the job')
    date_created = models.DateTimeField(
        auto_now_add=True, db_index=True,
        verbose_name='Creation DateTime',
        help_text='Datetime: creation date of the job')

    # Class attribute to be defined in child classes
    signature = None

    @staticmethod
    def check_parameters(parameters):
        """Checks that the parameters are valid for the current Job subclass"""
        raise NotImplementedError

    @staticmethod
    def make_task_parameters(parameters):
        """Returns the right task parameters from the request data"""
        raise NotImplementedError

    @classmethod
    def run(cls, parameters):
        """
        This method should be used to create jobs.
        It runs the linked Celery tasks and returns the corresponding Job instance.
        """
        # Launch the series of tasks
        # Returns an AsyncResult object for the first task in the series
        args, kwargs = cls.make_task_parameters(parameters)
        result = cls.signature.delay(*args, **kwargs)  # pylint: disable=no-member
        return cls(task_id=result.task_id)

    def get_current_task_result(self):
        """Get the AsyncResult of the currently running task"""
        current_result = AsyncResult(self.task_id)
        finished = False
        while current_result.ready():
            try:
                current_result = current_result.children[0]
            except IndexError:
                finished = True
                break
        return current_result, finished


class DownloadJob(Job):
    """
    Job which:
      - downloads a dataset
      - archives the result if necessary
      - publishes the result to an FTP server
    """
    class Meta:
        proxy = True

    @staticmethod
    def check_parameters(parameters):
        """
        Checks that the following parameters are present with correct values:
          - dataset_id: integer
        """
        if not set(parameters).issubset(set(('dataset_id', 'bounding_box'))):
            raise ValidationError("The download action accepts only one parameter: 'dataset_id'")
        if not isinstance(parameters['dataset_id'], int):
            raise ValidationError("'dataset_id' must be an integer")
        if ('bounding_box' in parameters and
                not (isinstance(parameters['bounding_box'], Sequence) and
                len(parameters['bounding_box']) == 4)):
            raise ValidationError("'bounding_box' must be a sequence in the following format: "
                                  "west, north, east, south")
        return parameters

    @staticmethod
    def make_task_parameters(parameters):
        return (((parameters['dataset_id'],),), {})

    @classmethod
    def run(cls, parameters):
        """
        This method should be used to create jobs.
        It runs the linked Celery tasks and returns the corresponding Job instance.
        """
        # Launch the series of tasks
        # Returns an AsyncResult object for the first task in the series
        args, kwargs = cls.make_task_parameters(parameters)
        signature = (
            tasks.download.signature(
                link=tasks.crop.signature(
                    kwargs={'bounding_box': parameters.get('bounding_box', None)},
                    link=tasks.archive.signature(
                        link=tasks.publish.signature())))
        ) if tasks else None
        result = signature.delay(*args, **kwargs)  # pylint: disable=no-member
        return cls(task_id=result.task_id)


class ConvertJob(Job):
    """
    Job which:
      - downloads a dataset
      - converts it into the given format
      - archives the result if necessary
      - publishes the result to an FTP server
    """
    class Meta:
        proxy = True

    @staticmethod
    def check_parameters(parameters):
        """
        Checks that the following parameters are present with correct values:
          - dataset_id: integer
          - format: value in ['idf']
        """
        accepted_keys = ('dataset_id', 'format', 'bounding_box')
        if not set(parameters).issubset(set(accepted_keys)):
            raise ValidationError(
                f"The download action accepts only these parameter: {', '.join(accepted_keys)}")

        if not isinstance(parameters['dataset_id'], int):
            raise ValidationError("'dataset_id' must be an integer")

        accepted_formats = ('idf',)
        if not parameters['format'] in accepted_formats:
            raise ValidationError(
                f"'format' only accepts the following values: {', '.join(accepted_formats)}")

        if ('bounding_box' in parameters and
                not (isinstance(parameters['bounding_box'], Sequence) and
                     len(parameters['bounding_box']) == 4)):
            raise ValidationError("'bounding_box' must be a sequence in the following format: "
                                  "west, north, east, south")

        return parameters

    @staticmethod
    def make_task_parameters(parameters):
        return (((parameters['dataset_id'],),), {})

    @classmethod
    def run(cls, parameters):
        """
        This method should be used to create jobs.
        It runs the linked Celery tasks and returns the corresponding Job instance.
        """
        # Launch the series of tasks
        # Returns an AsyncResult object for the first task in the series
        args, kwargs = cls.make_task_parameters(parameters)
        signature = (
            tasks.download.signature(
                link=tasks.crop.signature(
                    kwargs={'bounding_box': parameters.get('bounding_box', None)},
                    link=tasks.convert_to_idf.signature(
                        link=tasks.archive.signature(
                            link=tasks.publish.signature()))))
        ) if tasks else None
        result = signature.delay(*args, **kwargs)  # pylint: disable=no-member
        return cls(task_id=result.task_id)
