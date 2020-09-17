"""Models for the GeoSPaaS REST API"""
from django.db import models
from celery.result import AsyncResult
from rest_framework.exceptions import ValidationError


class Job(models.Model):
    """
    Intermediate model that gives access to the status and result of a series of linked celery tasks
    """

    task_id = models.CharField(
        unique=True, max_length=255,
        help_text='ID of the first task in the job')
    date_created = models.DateTimeField(
        auto_now_add=True, db_index=True,
        verbose_name='Creation DateTime',
        help_text='Datetime: creation date of the job')

    @classmethod
    def run(cls, signature, *args):
        """
        This method should be used to create jobs.
        It runs the linked celery tasks and returns the corresponding Job instance.
        """
        # Launch the series of tasks
        # Returns an AsyncResult object for the first task in the series
        result = signature.delay(*args)  # pylint: disable=no-member
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

    @staticmethod
    def validate_parameters(valid_parameters, parameters):
        """Validates the parameters of a request based on the valid_parameters dictionary."""
        # check that all parameter names from the request are valid
        for parameter, value in parameters.items():
            if parameter not in valid_parameters.keys():  # pylint: disable=no-member
                raise ValidationError(f"Invalid parameter '{parameter}'")
            # check that the parameter values are valid
            if 'type' in valid_parameters[parameter]:
                if not isinstance(value, valid_parameters[parameter]['type']):
                    raise ValidationError(f"Invalid value for '{parameter}'")
            elif 'values' in valid_parameters[parameter]:
                if not value in valid_parameters[parameter]['values']:
                    raise ValidationError(f"Invalid value for '{parameter}'")
        # check that all parameters are there
        if len(valid_parameters) != len(parameters):
            raise ValidationError(
                "All the following parameters are required: {}".format(
                    list(valid_parameters.keys())))  # pylint: disable=no-member
        return parameters
