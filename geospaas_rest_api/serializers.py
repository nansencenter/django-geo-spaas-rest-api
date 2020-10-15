"""
Serializers for the GeoSPaaS REST API
"""
from geospaas.catalog.models import (Dataset, DatasetRelationship, DatasetURI,
                                     GeographicLocation, Personnel, Role, Source)
from geospaas.vocabularies.models import DataCenter, Instrument, Parameter, Platform
from rest_framework import serializers


class GeographicLocationSerializer(serializers.ModelSerializer):
    """
    Serializer for GeographicLocation objects
    """
    class Meta:
        model = GeographicLocation
        fields = '__all__'


class SourceSerializer(serializers.ModelSerializer):
    """
    Serializer for Source objects
    """
    class Meta:
        model = Source
        fields = '__all__'


class InstrumentSerializer(serializers.ModelSerializer):
    """
    Serializer for Instrument objects
    """
    class Meta:
        model = Instrument
        fields = '__all__'


class PlatformSerializer(serializers.ModelSerializer):
    """
    Serializer for Source objects
    """
    class Meta:
        model = Platform
        fields = '__all__'


class PersonnelSerializer(serializers.ModelSerializer):
    """
    Serializer for Personnel objects
    """
    class Meta:
        model = Personnel
        fields = '__all__'


class RoleSerializer(serializers.ModelSerializer):
    """
    Serializer for Role objects
    """
    class Meta:
        model = Role
        fields = '__all__'


class DatasetSerializer(serializers.ModelSerializer):
    """
    Serializer for Dataset objects
    """
    class Meta:
        model = Dataset
        fields = '__all__'


class ParameterSerializer(serializers.ModelSerializer):
    """
    Serializer for Parameter objects
    """
    class Meta:
        model = Parameter
        fields = '__all__'


class DatasetURISerializer(serializers.ModelSerializer):
    """
    Serializer for DatasetURI objects
    """
    class Meta:
        model = DatasetURI
        fields = '__all__'


class DatasetRelationshipSerializer(serializers.ModelSerializer):
    """
    Serializer for DatasetRelationship objects
    """
    class Meta:
        model = DatasetRelationship
        fields = '__all__'


class DataCenterSerializer(serializers.ModelSerializer):
    """
    Serializer for DataCenter objects
    """
    class Meta:
        model = DataCenter
        fields = '__all__'
