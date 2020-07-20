"""
Serializers for the GeoSPaaS REST API
"""
import geospaas.catalog.models
import geospaas.vocabularies.models
import rest_framework.serializers


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
