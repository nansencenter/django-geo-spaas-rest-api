"""Processing API model classes"""
from rest_framework.exceptions import ValidationError
import geospaas_processing.tasks.syntool as tasks_syntool
import geospaas_processing.tasks.harvesting as tasks_harvesting
import geospaas_processing.tasks.idf as tasks_idf
import geospaas_processing.tasks.core as tasks_core
import celery
from collections.abc import Sequence
from celery.result import AsyncResult
from django.db import models


class Job(models.Model):
    """Base model that gives access to the status and result of
    running one or more Celery tasks.
    """
    # Database fields
    task_id = models.CharField(
        unique=True, max_length=255,
        help_text='ID of the last task in the job')
    date_created = models.DateTimeField(
        auto_now_add=True, db_index=True,
        verbose_name='Creation DateTime',
        help_text='Datetime: creation date of the job')

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
        if parameters.get('publish', False):
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
        if not set(parameters).issubset(set(('dataset_id', 'bounding_box', 'publish'))):
            raise ValidationError("The download action accepts only one parameter: 'dataset_id'")
        if not isinstance(parameters['dataset_id'], int):
            raise ValidationError("'dataset_id' must be an integer")
        if ('bounding_box' in parameters and
                not (isinstance(parameters['bounding_box'], Sequence) and
                     len(parameters['bounding_box']) == 4)):
            raise ValidationError("'bounding_box' must be a sequence in the following format: "
                                  "west, north, east, south")
        if ('publish' in parameters and not isinstance(parameters['publish'], bool)):
            raise ValidationError("'publish' must be a boolean")
        return parameters

    @staticmethod
    def make_task_parameters(parameters):
        return (((parameters['dataset_id'],),), {})


class ConvertJob(Job):  # pylint: disable=abstract-method
    """Parameters management methods for all conversion jobs
    """

    class Meta:
        proxy = True

    @classmethod
    def get_signature(cls, parameters):
        conversion_format = parameters['format']
        if conversion_format == 'idf':
            return celery.chain(
                tasks_core.download.signature(),
                tasks_core.unarchive.signature(),
                tasks_core.crop.signature(
                    kwargs={'bounding_box': parameters.get('bounding_box', None)}),
                tasks_idf.convert_to_idf.signature(),
                tasks_core.archive.signature(),
                tasks_core.publish.signature())
        elif conversion_format == 'syntool':
            syntool_chain = celery.chain(
                tasks_core.download.signature(),
                tasks_core.unarchive.signature(),
                tasks_core.crop.signature(
                    kwargs={'bounding_box': parameters.get('bounding_box', None)}),
                tasks_syntool.convert.signature(
                    kwargs={'converter_options': parameters.get('converter_options', None)}),
                tasks_syntool.db_insert.signature(),
                tasks_core.remove_downloaded.signature())
            if parameters.pop('skip_check', False):
                return syntool_chain
            else:
                return tasks_syntool.check_ingested.signature(kwargs={'to_execute': syntool_chain})
        else:
            raise RuntimeError(f"Unknown format {conversion_format}")

    @staticmethod
    def check_parameters(parameters):
        """Checks that the following parameters are present with
        correct values:
            - dataset_id: integer
            - bounding_box: 4-elements list
            - format: value in ['idf']
        """
        accepted_keys = ('dataset_id', 'format', 'bounding_box', 'skip_check', 'converter_options')
        if not set(parameters).issubset(set(accepted_keys)):
            raise ValidationError(
                f"The convert action accepts only these parameters: {', '.join(accepted_keys)}")

        if not isinstance(parameters['dataset_id'], int):
            raise ValidationError("'dataset_id' must be an integer")

        accepted_formats = ('idf', 'syntool')
        if not parameters['format'] in accepted_formats:
            raise ValidationError(
                f"'format' only accepts the following values: {', '.join(accepted_formats)}")

        if ('bounding_box' in parameters and
                not (isinstance(parameters['bounding_box'], Sequence) and
                     len(parameters['bounding_box']) == 4)):
            raise ValidationError("'bounding_box' must be a sequence in the following format: "
                                  "west, north, east, south")

        if ('converter_options' in parameters and
                not isinstance(parameters['converter_options'], dict)):
            raise ValidationError("'converter_options' should be a dictionary")

        return parameters

    @staticmethod
    def make_task_parameters(parameters):
        return (((parameters['dataset_id'],),), {})


class SyntoolCleanupJob(Job):
    """Job which cleans up ingested files older than a date"""
    class Meta:
        proxy = True

    @classmethod
    def get_signature(cls, parameters):
        return tasks_syntool.cleanup.signature()

    @staticmethod
    def check_parameters(parameters):
        accepted_keys = ('criteria',)
        if not set(parameters).issubset(accepted_keys):
            raise ValidationError(
                "The syntool cleanup action accepts only these parameters: " +
                str({', '.join(accepted_keys)}))

        try:
            if not isinstance(parameters['criteria'], dict):
                raise ValidationError("'criteria' must be a dictionary")
        except KeyError as error:
            raise ValidationError("The parameter 'criteria' is mandatory") from error

        return parameters

    @staticmethod
    def make_task_parameters(parameters):
        return ((parameters['criteria'],), {})


class SyntoolCompareJob(Job):
    """Job which generates comparison between Argo profiles and a 3D
    product
    """
    class Meta:
        proxy = True

    @classmethod
    def get_signature(cls, parameters):
        return celery.chain(
            tasks_syntool.compare_profiles.signature(),
            tasks_syntool.db_insert.signature(),
            tasks_core.remove_downloaded.signature(),
        )

    @staticmethod
    def check_parameters(parameters):
        accepted_keys = ('model', 'profiles')
        if not set(parameters) == set(accepted_keys):
            raise ValidationError(
                f"The convert action accepts only these parameters: {', '.join(accepted_keys)}")

        if ((not isinstance(parameters['model'], Sequence)) or
                len(parameters['model']) != 2 or
                not isinstance(parameters['model'][0], int) or
                not isinstance(parameters['model'][1], Sequence) or
                any((not isinstance(p, str) for p in parameters['model'][1]))):
            raise ValidationError("'model' must be a tuple (model_id, model_path)")

        valid_profiles = True
        if not isinstance(parameters['profiles'], Sequence):
            valid_profiles = False
        else:
            for profile_tuple in parameters['profiles']:
                if (not isinstance(profile_tuple, Sequence) or
                        len(profile_tuple) != 2 or
                        not isinstance(profile_tuple[0], int) or
                        not isinstance(profile_tuple[1], Sequence) or
                        any((not isinstance(p, str) for p in profile_tuple[1]))):
                    valid_profiles = False
                    break
        if not valid_profiles:
            raise ValidationError("'profiles' must be a list of tuples (profile_id, profile_path)")
        return parameters

    @staticmethod
    def make_task_parameters(parameters):
        return (((parameters['model'], parameters['profiles']),), {})


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
