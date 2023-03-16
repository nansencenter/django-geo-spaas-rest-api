"""Base model classes"""
from celery.result import AsyncResult
from django.db import models


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
