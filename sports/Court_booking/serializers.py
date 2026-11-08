from rest_framework import serializers
from .models import Court

class booking_serializer(serializers.ModelSerializer):
    class Meta:
        model = Court
        fields = '__all__'