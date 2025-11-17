from rest_framework import serializers
from .models import WaterUnit, WaterQuality, Maintenance, Maintainer


class MaintainerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Maintainer
        fields = ['id', 'name', 'email']


class RegisterMaintainerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Maintainer
        fields = ['id', 'name', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        return Maintainer.objects.create_user(
            email=validated_data['email'],
            name=validated_data['name'],
            password=validated_data['password']
        )


class WaterUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = WaterUnit
        fields = '__all__'


class WaterQualitySerializer(serializers.ModelSerializer):
    class Meta:
        model = WaterQuality
        fields = '__all__'
        read_only_fields = ["date_time"]


class MaintenanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Maintenance
        fields = '__all__'
        extra_kwargs = {
            'datetime': {'required': False},
        }

