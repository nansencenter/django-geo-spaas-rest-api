"""Serializers for the processing API"""
import rest_framework.serializers
import celery.result
import django_celery_results.models
import geospaas_processing.models

import geospaas_rest_api.models as models

class JobSerializer(rest_framework.serializers.Serializer):
    """Serializer for Job objects"""

    jobs = {
        'download': models.DownloadJob,
        'convert': models.ConvertJob,
        'harvest': models.HarvestJob,
        'syntool_cleanup': models.SyntoolCleanupJob,
        'compare_profiles': models.SyntoolCompareJob,
    }

    # Actual Job fields
    id = rest_framework.serializers.IntegerField(read_only=True)
    task_id = rest_framework.serializers.CharField(read_only=True)
    date_created = rest_framework.serializers.DateTimeField(read_only=True)

    # Fields used to launch jobs
    action = rest_framework.serializers.ChoiceField(
        choices=[
            'download',
            'convert',
            'harvest',
            'syntool_cleanup',
            'compare_profiles',
        ],
        required=True, write_only=True,
        help_text="Action to perform")
    parameters = rest_framework.serializers.DictField(write_only=True,
                                                      help_text="Parameters for the action")

    def to_representation(self, instance):
        """Generate a representation of the job"""
        representation = super().to_representation(instance)

        current_result, finished = instance.get_current_task_result()
        if isinstance(current_result, celery.result.AsyncResult):
            representation['status'] = current_result.state
        elif isinstance(current_result, celery.result.ResultSet):
            representation['status'] = {
                r.task_id: r.state
                for r in current_result
            }

        if finished:
            representation['date_done'] = current_result.date_done
            if current_result.state == 'SUCCESS':
                representation['result'] = current_result.result
            elif current_result.state == 'FAILURE':
                representation['result'] = current_result.traceback

        return representation

    def update(self, instance, validated_data):
        """Does nothing. Update of already created tasks is only done by the Celery worker"""

    @classmethod
    def choose_job_class(cls, data):
        """Return the right job class based on the request data
        """
        return cls.jobs[data['action']]

    def create(self, validated_data):
        """Launches a long-running task, and returns the corresponding AsyncResult"""
        # choose the right Job class
        job = self.choose_job_class(validated_data).run(validated_data['parameters'])
        job.save()
        return job

    def validate(self, attrs):
        """Validates the request data"""
        # No need to check for the presence of 'action' and 'parameters',
        # because fields are checked before this method comes into play
        attrs['parameters'] = self.choose_job_class(attrs).check_parameters(attrs['parameters'])
        return attrs


class TaskResultSerializer(rest_framework.serializers.ModelSerializer):
    """Serializer for TaskResult objects"""
    class Meta:
        model = django_celery_results.models.TaskResult
        fields = '__all__'


class ProcessingResultSerializer(rest_framework.serializers.ModelSerializer):
    """Serializer for ProcessingResult objects"""
    class Meta:
        model = geospaas_processing.models.ProcessingResult
        fields = '__all__'
