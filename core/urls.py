from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.search_donors, name='search_donors'),
    path('search/', views.search_donors, name='search_donors'),

    path('register/', views.register_donor, name='register_donor'),
    path('login/', views.donor_login, name='donor_login'),
    path('logout/', views.donor_logout, name='donor_logout'),

    path(
        'availability/',
        views.update_availability,
        name='update_availability'
    ),
    path(
        'profile/edit/',
        views.edit_profile,
        name='edit_profile'
    ),

    path(
        'donation-history/',
        views.donation_history,
        name='donation_history'
    ),

    path(
        'volunteer/register/',
        views.register_volunteer,
        name='register_volunteer'
    ),
    path(
        'volunteer/dashboard/',
        views.volunteer_dashboard,
        name='volunteer_dashboard'
    ),

    path(
        'blood-request/create/',
        views.create_blood_request,
        name='create_blood_request'
    ),
    path(
        'blood-requests/my/',
        views.my_blood_requests,
        name='my_blood_requests'
    ),

    path(
        'blood-requests/incoming/',
        views.incoming_blood_requests,
        name='incoming_blood_requests'
    ),

    path(
        'blood-requests/<int:request_id>/accept/',
        views.accept_blood_request,
        name='accept_blood_request'
    ),
    path(
        'blood-requests/<int:request_id>/reject/',
        views.reject_blood_request,
        name='reject_blood_request'
    ),
    path(
        'blood-requests/<int:request_id>/complete/',
        views.complete_blood_request,
        name='complete_blood_request'
    ),

    # REST API URLs
    path('api/', include('core.api_urls')),
]




