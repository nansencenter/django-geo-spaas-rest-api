"""Models for the GeoSPaaS REST API"""
from django.db import models
from celery.result import AsyncResult


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
