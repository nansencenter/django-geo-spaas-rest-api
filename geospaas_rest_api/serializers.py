"""
Serializers for the GeoSPaaS REST API
"""
import json

import geospaas.catalog.models
import geospaas.vocabularies.models
import rest_framework.serializers
from rest_framework.exceptions import ValidationError

try:
    import geospaas_processing.tasks as tasks
except ImportError:
    tasks = None


class TaskResultSerializer(rest_framework.serializers.Serializer):
    """Serializer for TaskResult objects"""

    # Fields from the TaskResult model; used to display tasks
    task_id = rest_framework.serializers.CharField(read_only=True)
    task_name = rest_framework.serializers.CharField(read_only=True)
    result = rest_framework.serializers.CharField(read_only=True)
    status = rest_framework.serializers.CharField(read_only=True)
    task_args = rest_framework.serializers.CharField(read_only=True)
    date_created = rest_framework.serializers.DateTimeField(read_only=True)
    date_done = rest_framework.serializers.DateTimeField(read_only=True)
    meta = rest_framework.serializers.CharField(read_only=True)

    # Fields used to launch tasks
    action = rest_framework.serializers.ChoiceField(choices=['download', 'convert'],
                                                    required=True, write_only=True,
                                                    help_text="Action to perform")
    parameters = rest_framework.serializers.DictField(write_only=True,
                                                      help_text="Parameters for the action")

    def __init__(self, *args, **kwargs):
        """
        Check for geospaas_processing.tasks availability
        before allowing to instantiate the serializer
        """
        if not tasks:
            raise ImportError('geospaas_processing.tasks is not available')
        super().__init__(*args, **kwargs)

    def to_representation(self, instance):
        """Adapt representation of result and meta fields"""
        representation = super().to_representation(instance)
        representation['result'] = json.loads(representation['result'])
        representation['meta'] = json.loads(representation['meta'])
        return representation

    def update(self, instance, validated_data):
        """Does nothing. Update of already created tasks is only done by Celery"""

    def create(self, validated_data):
        """Launches a long-running task, and returns the corresponding AsyncResult"""
        if validated_data['action'] == 'download':
            result = tasks.download.delay(validated_data['parameters']['dataset_id'])
        elif validated_data['action'] == 'convert':
            if validated_data['parameters']['format'].lower() == 'idf':
                result = tasks.download.apply_async(
                    (validated_data['parameters']['dataset_id'],),
                    link=tasks.convert_to_idf.s())
        return result

    def validate(self, attrs):
        """
        Validates the parameters of a request based on the valid_parameters dictionary.
        The keys of this dictionary are the valid values for the `action` field.
        For each of these actions, the value is a dictionary of valid parameters associated with
        the type or valid values for this parameter. To sum up:

        valid_parameters = {
            'action_name': {
                'parameter1_name': {'type': int},
                'parameter2_name': {'values': ['value1', 'value2']}
            },
            ...
        }
        """
        valid_parameters = {
            'download': {'dataset_id': {'type': int}},
            'convert': {
                'dataset_id': {'type': int},
                'format': {'values': ['idf']}
            }
        }

        # No need to check for the presence of 'action' and 'parameters',
        # because fields are checked before this method comes into play
        req_action = attrs['action']
        req_parameters = attrs['parameters']

        action_parameters = valid_parameters[req_action]
        # check that all parameter names from the request are valid
        for parameter, value in req_parameters.items():
            if parameter not in action_parameters.keys():
                raise ValidationError(
                    "The valid parameters for the '{}' action are: {}".format(
                        req_action, list(action_parameters.keys())))
            # check that the parameter values are valid
            if 'type' in action_parameters[parameter]:
                if not isinstance(value, action_parameters[parameter]['type']):
                    raise ValidationError(f"Invalid {parameter}")
            elif 'values' in action_parameters[parameter]:
                if not value in action_parameters[parameter]['values']:
                    raise ValidationError(f"Invalid {parameter}")
        # check that all parameters are there
        if len(action_parameters) != len(req_parameters):
            raise ValidationError(
                "All the following parameters are required for action '{}': {}".format(
                    req_action, list(action_parameters.keys())))
        return attrs


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


class DatasetParameterSerializer(rest_framework.serializers.ModelSerializer):
    """Serializer for DatasetParameter objects"""
    class Meta:
        model = geospaas.catalog.models.DatasetParameter
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
