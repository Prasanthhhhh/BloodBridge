from rest_framework import serializers
from .models import DonorProfile, BloodRequest


class DonorSerializer(serializers.ModelSerializer):

    class Meta:
        model = DonorProfile
        fields = [
            'id',
            'full_name',
            'blood_group',
            'city',
            'is_available',
        ]

        read_only_fields = ['id']


class BloodRequestSerializer(serializers.ModelSerializer):

    units_needed = serializers.IntegerField(min_value=1)

    class Meta:
        model = BloodRequest
        fields = [
            'id',
            'patient_name',
            'contact_phone',
            'blood_group',
            'city',
            'hospital_name',
            'units_needed',
            'urgency',
            'details',
            'status',
            'created_at',
        ]

        read_only_fields = [
            'id',
            'status',
            'created_at',
        ]