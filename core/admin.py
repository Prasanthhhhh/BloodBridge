
from django.contrib import admin
from .models import DonorProfile, BloodRequest, DonationHistory


@admin.register(DonorProfile)
class DonorProfileAdmin(admin.ModelAdmin):
    list_display = (
        'full_name',
        'blood_group',
        'city',
        'phone',
        'is_available',
    )

    search_fields = (
        'full_name',
        'user__username',
        'blood_group',
        'city',
        'phone',
    )

    list_filter = ('blood_group', 'city', 'is_available')


@admin.register(BloodRequest)
class BloodRequestAdmin(admin.ModelAdmin):
    list_display = (
        'patient_name',
        'blood_group',
        'city',
        'hospital_name',
        'status',
        'urgency',
        'created_at',
    )

    search_fields = (
        'patient_name',
        'blood_group',
        'city',
        'hospital_name',
    )

    list_filter = (
        'blood_group',
        'city',
        'status',
        'urgency',
    )


@admin.register(DonationHistory)
class DonationHistoryAdmin(admin.ModelAdmin):
    list_display = (
        'donor',
        'blood_group',
        'hospital_name',
        'city',
        'units_donated',
        'donation_date',
    )

    search_fields = (
        'donor__full_name',
        'donor__user__username',
        'blood_group',
        'city',
        'hospital_name',
    )

    list_filter = (
        'blood_group',
        'city',
        'donation_date',
    )
