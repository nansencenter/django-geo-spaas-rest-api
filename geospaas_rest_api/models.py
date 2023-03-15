"""Models for the GeoSPaaS REST API"""
from collections.abc import Sequence
import functools
import types
try:
    import geospaas_processing.tasks.core as tasks_core
except ImportError as error:
    tasks_core = error.name

try:
    import geospaas_processing.tasks.idf as tasks_idf
except ImportError as error:
    tasks_idf = error.name

try:
    import geospaas_processing.tasks.harvesting as tasks_harvesting
except ImportError as error:
    tasks_harvesting = error.name

try:
    import geospaas_processing.tasks.syntool as tasks_syntool
except ImportError as error:
    tasks_syntool = error.name

import celery
import dateutil.parser
from celery.result import AsyncResult
from django.db import models
from rest_framework.exceptions import ValidationError


def requires_func_decorator(*dependencies):
    """Function decorator which raises an exception if a required
    module is not available
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            missing_dependencies = []
            for dependency in dependencies:
                if not isinstance(dependency, types.ModuleType):
                    missing_dependencies.append(dependency)
            if missing_dependencies:
                raise ImportError(f"{', '.join(d for d in missing_dependencies)} unavailable")
            return func(*args, **kwargs)
        return wrapper
    return decorator


def requires(*dependencies):
    """Class decorator which applies requires_func_decorator() to the
    __init__ method of a class
    """
    def decorator(cls):
        cls.__init__ = requires_func_decorator(*dependencies)(cls.__init__)
        return cls
    return decorator


class Job(models.Model):
    """Base model that gives access to the status and result of
    running one or more Celery tasks.
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

    @classmethod
    def get_signature(cls, parameters):
        """Returns a Celery signature which will be executed when the
        job is run. Can be one task or several organized using a
        canvas.
        See https://docs.celeryq.dev/en/stable/userguide/canvas.html
        """
        raise NotImplementedError

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
        """This method should be used to create jobs.
        Should return a Job instance.
        """
        args, kwargs = cls.make_task_parameters(parameters)
        result = cls.get_signature(parameters).delay(*args, **kwargs)
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


@requires(tasks_core)
class DownloadJob(Job):
    """
    Job which:
      - downloads a dataset
      - archives the result if necessary
      - publishes the result to an FTP server
    """
    class Meta:
        proxy = True

    @classmethod
    def get_signature(cls, parameters):
        tasks = [tasks_core.download.signature()]

        # only unarchive if cropping is needed
        bounding_box = parameters.get('bounding_box', None)
        if bounding_box:
            tasks.extend([
                tasks_core.unarchive.signature(),
                tasks_core.crop.signature(
                    kwargs={'bounding_box': parameters.get('bounding_box', None)}),
            ])

        tasks.extend([
            tasks_core.archive.signature(),
            tasks_core.publish.signature(),
        ])
        return celery.chain(tasks)

    @staticmethod
    def check_parameters(parameters):
        """
        Checks that the following parameters are present with correct values:
            - dataset_id: integer
            - bounding_box: 4-elements list
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


class ConvertJob(Job):  # pylint: disable=abstract-method
    """Parameters management methods for all conversion jobs
    """

    class Meta:
        proxy = True

    @staticmethod
    def check_parameters(parameters):
        """Checks that the following parameters are present with
        correct values:
            - dataset_id: integer
            - bounding_box: 4-elements list
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


@requires(tasks_core, tasks_idf)
class IDFConvertJob(ConvertJob):
    """Job which:
      - downloads a dataset
      - converts it into the given format
      - archives the result if necessary
      - publishes the result to an FTP server
    """
    class Meta:
        proxy = True

    @classmethod
    def get_signature(cls, parameters):
        return celery.chain(
            tasks_core.download.signature(),
            tasks_core.unarchive.signature(),
            tasks_core.crop.signature(
                kwargs={'bounding_box': parameters.get('bounding_box', None)}),
            tasks_idf.convert_to_idf.signature(),
            tasks_core.archive.signature(),
            tasks_core.publish.signature())


@requires(tasks_core, tasks_syntool)
class SyntoolConvertJob(ConvertJob):
    """Job which converts a dataset into Syntool-displayable data
    """
    class Meta:
        proxy = True

    @classmethod
    def get_signature(cls, parameters):
        return (
            tasks_syntool.check_ingested.signature(),
            tasks_core.download.signature(),
            tasks_core.unarchive.signature(),
            tasks_core.crop.signature(
                kwargs={'bounding_box': parameters.get('bounding_box', None)}),
            tasks_syntool.convert.signature(),
            tasks_syntool.db_insert.signature(),
            tasks_core.remove_downloaded.signature()
        )


@requires(tasks_syntool)
class SyntoolCleanupJob(Job):
    """Job which cleans up ingested files older than a date"""
    class Meta:
        proxy = True

    @classmethod
    def get_signature(cls, parameters):
        return tasks_syntool.cleanup_ingested.signature()

    @staticmethod
    def check_parameters(parameters):
        accepted_keys = ('date', 'created')
        if not set(parameters).issubset(accepted_keys):
            raise ValidationError(
                "The syntool cleanup action accepts only these parameter: " +
                str({', '.join(accepted_keys)}))

        try:
            dateutil.parser.parse(parameters['date'])
        except KeyError:
            raise ValidationError("The date parameter is mandatory")
        except dateutil.parser.ParserError as error:
            raise ValidationError("'date' must be a valid date string") from error

        if not isinstance(parameters.get('created', False), bool): # default is just a placeholder
            raise ValidationError("'created' must be a boolean")

        return parameters

    @staticmethod
    def make_task_parameters(parameters):
        return (
            (dateutil.parser.parse(parameters['date']),),
            {'created': parameters.get('created', False)})


@requires(tasks_harvesting)
class HarvestJob(Job):
    """Job which harvests metadata into the database"""
    class Meta:
        proxy = True

    @classmethod
    def get_signature(cls, parameters):
        return tasks_harvesting.start_harvest.signature()

    @staticmethod
    def check_parameters(parameters):
        if tuple(parameters.keys()) != ('search_config_dict',):
            raise ValidationError('Only parameter accepted: "search_config_dict"')
        if not isinstance(parameters['search_config_dict'], dict):
            raise ValidationError('search_config_dict should be a dict')
        return parameters

    @staticmethod
    def make_task_parameters(parameters):
        return ((parameters['search_config_dict'],), {})
