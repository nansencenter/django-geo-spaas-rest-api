"""Serializers for the base geospaas API"""
import geospaas.catalog.models
import geospaas.vocabularies.models
import rest_framework.serializers


class KeywordSerializer(rest_framework.serializers.ModelSerializer):
    """Serializer for Keyword objects"""
    class Meta:
        model = geospaas.vocabularies.models.Keyword
        fields = '__all__'


class ParameterSerializer(rest_framework.serializers.ModelSerializer):
    """
    Serializer for Parameter objects
    """
    class Meta:
        model = geospaas.vocabularies.models.Parameter
        fields = '__all__'


class TagSerializer(rest_framework.serializers.ModelSerializer):
    """Serializer for Tag objects"""
    class Meta:
        model = geospaas.catalog.models.Tag
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
