"""
API v1 serializers.
"""
from rest_framework import serializers


class BaseSerializer(serializers.ModelSerializer):
    """
    Base serializer for all models.
    """
    class Meta:
        fields = '__all__'
