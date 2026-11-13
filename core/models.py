from django.db import models
from django.contrib.auth.models import User


class DonorProfile(models.Model):
    BLOOD_GROUPS = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=150, blank=True, default='')
    phone = models.CharField(max_length=15)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUPS)
    city = models.CharField(max_length=100)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.full_name or self.user.username


class VolunteerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=15)
    city = models.CharField(max_length=100)
    registered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name


class BloodRequest(models.Model):
    BLOOD_GROUPS = DonorProfile.BLOOD_GROUPS

    URGENCY_CHOICES = [
        ('normal', 'Normal'),
        ('urgent', 'Urgent'),
        ('emergency', 'Emergency'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    requester = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='blood_requests'
    )

    accepted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='accepted_blood_requests'
    )

    # Track donors who rejected this blood request
    rejected_by = models.ManyToManyField(
        User,
        blank=True,
        related_name='rejected_blood_requests'
    )

    patient_name = models.CharField(max_length=150)
    contact_phone = models.CharField(max_length=15)

    blood_group = models.CharField(
        max_length=3,
        choices=BLOOD_GROUPS
    )

    city = models.CharField(max_length=100)
    hospital_name = models.CharField(max_length=200)
    units_needed = models.PositiveSmallIntegerField(default=1)

    urgency = models.CharField(
        max_length=10,
        choices=URGENCY_CHOICES,
        default='normal'
    )

    details = models.TextField(blank=True)

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f'{self.blood_group} request - '
            f'{self.patient_name}'
        )

class DonationHistory(models.Model):
    donor = models.ForeignKey(
        DonorProfile,
        on_delete=models.CASCADE,
        related_name='donation_history'
    )

    blood_group = models.CharField(
        max_length=3,
        choices=DonorProfile.BLOOD_GROUPS
    )

    hospital_name = models.CharField(max_length=200)

    city = models.CharField(max_length=100)

    units_donated = models.PositiveSmallIntegerField(default=1)

    donation_date = models.DateField()

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f'{self.donor.full_name or self.donor.user.username} - '
            f'{self.blood_group} - {self.donation_date}'
        )


