from rest_framework import serializers


class BaseSerializer(serializers.ModelSerializer):
    """
    Base serializer that standardizes read-only timestamp fields.
    """

    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        abstract = True