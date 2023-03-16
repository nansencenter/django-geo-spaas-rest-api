"""Jobs that rely on geospaas_processing"""
from collections.abc import Sequence

import celery
import dateutil.parser
import geospaas_processing.tasks.core as tasks_core
import geospaas_processing.tasks.idf as tasks_idf
import geospaas_processing.tasks.harvesting as tasks_harvesting
import geospaas_processing.tasks.syntool as tasks_syntool
from rest_framework.exceptions import ValidationError

from .base import Job


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
            return celery.chain(
                tasks_syntool.check_ingested.signature(),
                tasks_core.download.signature(),
                tasks_core.unarchive.signature(),
                tasks_core.crop.signature(
                    kwargs={'bounding_box': parameters.get('bounding_box', None)}),
                tasks_syntool.convert.signature(),
                tasks_syntool.db_insert.signature(),
                tasks_core.remove_downloaded.signature())
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
        accepted_keys = ('dataset_id', 'format', 'bounding_box')
        if not set(parameters).issubset(set(accepted_keys)):
            raise ValidationError(
                f"The download action accepts only these parameters: {', '.join(accepted_keys)}")

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
        return tasks_syntool.cleanup_ingested.signature()

    @staticmethod
    def check_parameters(parameters):
        accepted_keys = ('date', 'created')
        if not set(parameters).issubset(accepted_keys):
            raise ValidationError(
                "The syntool cleanup action accepts only these parameters: " +
                str({', '.join(accepted_keys)}))

        try:
            dateutil.parser.parse(parameters['date'])
        except KeyError as error:
            raise ValidationError("The date parameter is mandatory") from error
        except dateutil.parser.ParserError as error:
            raise ValidationError("'date' must be a valid date string") from error

        if not isinstance(parameters.get('created', False), bool):  # default is just a placeholder
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
