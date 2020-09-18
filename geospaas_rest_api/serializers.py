"""
Serializers for the GeoSPaaS REST API
"""
import django_celery_results.models
import geospaas.catalog.models
import geospaas.vocabularies.models
import rest_framework.serializers

import geospaas_rest_api.models as models


class JobSerializer(rest_framework.serializers.Serializer):
    """Serializer for Job objects"""

    jobs = {
        'download': models.DownloadJob,
        'convert': models.ConvertJob
    }

    # Actual Job fields
    id = rest_framework.serializers.IntegerField(read_only=True)
    task_id = rest_framework.serializers.CharField(read_only=True)
    date_created = rest_framework.serializers.DateTimeField(read_only=True)

    # Fields used to launch jobs
    action = rest_framework.serializers.ChoiceField(choices=list(jobs.keys()),
                                                    required=True, write_only=True,
                                                    help_text="Action to perform")
    parameters = rest_framework.serializers.DictField(write_only=True,
                                                      help_text="Parameters for the action")

    def to_representation(self, instance):
        """Generate a representation of the job"""
        representation = super().to_representation(instance)

        current_result, finished = instance.get_current_task_result()
        representation['status'] = current_result.state

        if finished:
            representation.update({
                'date_done': current_result.date_done,
                'result': current_result.result
            })

        return representation

    def update(self, instance, validated_data):
        """Does nothing. Update of already created tasks is only done by the Celery worker"""

    def create(self, validated_data):
        """Launches a long-running task, and returns the corresponding AsyncResult"""
        # This might need to be modified if the first task of a Job requires more arguments
        job = self.jobs[validated_data['action']].run((validated_data['parameters']['dataset_id'],))
        job.save()
        return job

    def validate(self, attrs):
        """Validates the request data"""
        # No need to check for the presence of 'action' and 'parameters',
        # because fields are checked before this method comes into play
        attrs['parameters'] = self.jobs[attrs['action']].check_parameters(
            attrs['parameters']
        )
        return attrs


class TaskResultSerializer(rest_framework.serializers.ModelSerializer):
    """Serializer for TaskResult objects"""
    class Meta:
        model = django_celery_results.models.TaskResult
        fields = '__all__'


class GeographicLocationSerializer(rest_framework.serializers.ModelSerializer):
    """Serializer for GeographicLocation objects"""
    class Meta:
        model = geospaas.catalog.models.GeographicLocation
        fields = '__all__'


class SourceSerializer(rest_framework.serializers.ModelSerializer):
    """Serializer for Source objects"""
    class Meta:
        model = geospaas.catalog.models.Source
        fields = '__all__'


class InstrumentSerializer(rest_framework.serializers.ModelSerializer):
    """Serializer for Instrument objects"""
    class Meta:
        model = geospaas.vocabularies.models.Instrument
        fields = '__all__'


class PlatformSerializer(rest_framework.serializers.ModelSerializer):
    """Serializer for Source objects"""
    class Meta:
        model = geospaas.vocabularies.models.Platform
        fields = '__all__'


class PersonnelSerializer(rest_framework.serializers.ModelSerializer):
    """Serializer for Personnel objects"""
    class Meta:
        model = geospaas.catalog.models.Personnel
        fields = '__all__'


class RoleSerializer(rest_framework.serializers.ModelSerializer):
    """Serializer for Role objects"""
    class Meta:
        model = geospaas.catalog.models.Role
        fields = '__all__'


class DatasetSerializer(rest_framework.serializers.ModelSerializer):
    """Serializer for Dataset objects"""
    class Meta:
        model = geospaas.catalog.models.Dataset
        fields = '__all__'


class ParameterSerializer(rest_framework.serializers.ModelSerializer):
    """
    Serializer for Parameter objects
    """
    class Meta:
        model = geospaas.vocabularies.models.Parameter
        fields = '__all__'


class DatasetURISerializer(rest_framework.serializers.ModelSerializer):
    """Serializer for DatasetURI objects"""
    class Meta:
        model = geospaas.catalog.models.DatasetURI
        fields = '__all__'


class DatasetRelationshipSerializer(rest_framework.serializers.ModelSerializer):
    """Serializer for DatasetRelationship objects"""
    class Meta:
        model = geospaas.catalog.models.DatasetRelationship
        fields = '__all__'


class DataCenterSerializer(rest_framework.serializers.ModelSerializer):
    """Serializer for DataCenter objects"""
    class Meta:
        model = geospaas.vocabularies.models.DataCenter
        fields = '__all__'
