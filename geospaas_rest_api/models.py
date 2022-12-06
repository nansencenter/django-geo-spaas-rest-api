"""Models for the GeoSPaaS REST API"""
try:
    import geospaas_processing.tasks.core as tasks_core
except ImportError:
    tasks_core = None

try:
    import geospaas_processing.tasks.idf as tasks_idf
except ImportError:
    tasks_idf = None

try:
    import geospaas_processing.tasks.harvesting as tasks_harvesting
except ImportError:
    tasks_harvesting = None

try:
    import geospaas_processing.tasks.syntool as tasks_syntool
except ImportError:
    tasks_syntool = None

import dateutil.parser
from celery.result import AsyncResult, GroupResult, ResultSet
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

    signature = (
        tasks_core.download.signature(
            link=tasks_core.archive.signature(
                link=tasks_core.publish.signature()))
    ) if tasks_idf else None

    def __init__(self, *args, **kwargs):
        if not tasks_core:
            raise ImportError('geospaas_processing.tasks.core is not available')
        super().__init__(*args, **kwargs)

    @staticmethod
    def check_parameters(parameters):
        """Checks that the following parameters are present with
        correct values:
          - dataset_id: integer
        """
        if not set(parameters) == set(('dataset_id',)):
            raise ValidationError("The download action accepts only one parameter: 'dataset_id'")
        if not isinstance(parameters['dataset_id'], int):
            raise ValidationError("'dataset_id' must be an integer")
        return parameters

    @staticmethod
    def make_task_parameters(parameters):
        return (((parameters['dataset_id'],),), {})


class ConvertJob(Job):
    """Parameters management methods for all conversion jobs
    """
    @staticmethod
    def check_parameters(parameters):
        """Checks that the following parameters are present with
        correct values:
          - dataset_id: integer
          - format: value in ['idf']
        """
        accepted_keys = ('dataset_id', 'format')
        if not set(parameters) == set(accepted_keys):
            raise ValidationError(
                f"The download action accepts only these parameter: {', '.join(accepted_keys)}")

        if not isinstance(parameters['dataset_id'], int):
            raise ValidationError("'dataset_id' must be an integer")

        accepted_formats = ('idf', 'syntool')
        if not parameters['format'] in accepted_formats:
            raise ValidationError(
                f"'format' only accepts the following values: {', '.join(accepted_formats)}")

        return parameters

    @staticmethod
    def make_task_parameters(parameters):
        return (((parameters['dataset_id'],),), {})


class IDFConvertJob(ConvertJob):
    """Job which:
      - downloads a dataset
      - converts it into the given format
      - archives the result if necessary
      - publishes the result to an FTP server
    """
    class Meta:
        proxy = True

    signature = (
        tasks_core.download.signature(
            link=tasks_idf.convert_to_idf.signature(
                link=tasks_core.archive.signature(
                    link=tasks_core.publish.signature())))
    ) if tasks_idf and tasks_core else None

    def __init__(self, *args, **kwargs):
        if not (tasks_idf and tasks_core):
            raise ImportError('geospaas_processing.tasks.idf or core is not available')
        super().__init__(*args, **kwargs)


class SyntoolConvertJob(ConvertJob):
    """Job which converts a dataset into Syntool-displayable data
    """
    class Meta:
        proxy = True

    signature = (
        tasks_syntool.check_ingested.signature(
            link=tasks_core.download.signature(
                link=tasks_syntool.convert.signature(
                    link=tasks_syntool.db_insert.signature(
                        link=tasks_core.remove_downloaded.signature()))))
    ) if tasks_syntool and tasks_core else None

    def __init__(self, *args, **kwargs):
        if not (tasks_syntool and tasks_core):
            raise ImportError('geospaas_processing.tasks.syntool or core is not available')
        super().__init__(*args, **kwargs)


class SyntoolCleanupJob(Job):
    """Job whic cleans up ingested files older than a date"""
    class Meta:
        proxy = True

    signature = tasks_syntool.cleanup_ingested.signature() if tasks_syntool else None

    def __init__(self, *args, **kwargs):
        if not tasks_syntool:
            raise ImportError('geospaas_processing.tasks.syntool is not available')
        super().__init__(*args, **kwargs)

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


class HarvestJob(Job):
    """Job which harvests metadata into the database"""
    class Meta:
        proxy = True

    signature = (
        tasks_harvesting.start_harvest.signature()
    ) if tasks_harvesting else None

    def __init__(self, *args, **kwargs):
        if not tasks_harvesting:
            raise ImportError('geospaas_processing.tasks.harvesting is not available')
        super().__init__(*args, **kwargs)

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
