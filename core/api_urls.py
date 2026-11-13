from django.urls import path
from .api_views import (
    DonorListAPIView,
    BloodRequestListCreateAPIView,
    BloodRequestDetailAPIView,
)

urlpatterns = [
    path(
        'donors/',
        DonorListAPIView.as_view(),
        name='api_donors'
    ),

    path(
        'blood-requests/',
        BloodRequestListCreateAPIView.as_view(),
        name='api_blood_requests'
    ),

    path(
        'blood-requests/<int:pk>/',
        BloodRequestDetailAPIView.as_view(),
        name='api_blood_request_detail'
    ),
]
