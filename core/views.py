

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.mail import send_mail

from .models import (
    DonorProfile,
    VolunteerProfile,
    BloodRequest,
    DonationHistory,
)

from .forms import (
    DonorRegistrationForm,
    DonorProfileForm,
    VolunteerRegistrationForm,
    BloodRequestForm,
)


def send_notification_email(subject, message, recipient_email):
    """Send an email only when the recipient has an email address."""
    if not recipient_email:
        return False

    try:
        send_mail(
            subject,
            message,
            None,
            [recipient_email],
            fail_silently=True,
        )
        return True
    except Exception:
        return False


def search_donors(request):
    blood_group = request.GET.get('blood_group', '').strip()
    city = request.GET.get('city', '').strip()
    availability = request.GET.get('availability', 'available').strip()

    if availability == 'available':
        donors = DonorProfile.objects.filter(is_available=True)
    elif availability == 'unavailable':
        donors = DonorProfile.objects.filter(is_available=False)
    else:
        donors = DonorProfile.objects.all()
        availability = 'all'

    if request.user.is_authenticated:
        donors = donors | DonorProfile.objects.filter(user=request.user)

    if blood_group:
        donors = donors.filter(blood_group=blood_group)

    if city:
        donors = donors.filter(city__iexact=city)

    cities = list(
        DonorProfile.objects
        .filter(is_available=True)
        .values_list('city', flat=True)
        .distinct()
        .order_by('city')
    )

    total_donors = DonorProfile.objects.count()

    available_donors = DonorProfile.objects.filter(
        is_available=True
    ).count()

    pending_requests = BloodRequest.objects.filter(
        status='pending'
    ).count()

    completed_requests = BloodRequest.objects.filter(
        status='completed'
    ).count()

    context = {
        'donors': donors.distinct(),
        'blood_groups': DonorProfile.BLOOD_GROUPS,
        'selected_blood_group': blood_group,
        'city': city,
        'cities': cities,
        'availability': availability,
        'total_donors': total_donors,
        'available_donors': available_donors,
        'pending_requests': pending_requests,
        'completed_requests': completed_requests,
    }

    return render(request, 'core/search_donors.html', context)


def register_donor(request):
    if request.method == 'POST':
        form = DonorRegistrationForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            if User.objects.filter(username=username).exists():
                form.add_error(
                    'username',
                    'This username is already taken.'
                )
            else:
                with transaction.atomic():
                    user = User.objects.create_user(
                        username=username,
                        password=password
                    )

                    DonorProfile.objects.create(
                        user=user,
                        full_name=form.cleaned_data['full_name'].strip(),
                        phone=form.cleaned_data['phone'],
                        blood_group=form.cleaned_data['blood_group'],
                        city=form.cleaned_data['city'].strip(),
                    )

                messages.success(
                    request,
                    'Donor registration successful! Please log in.'
                )
                return redirect('donor_login')
    else:
        form = DonorRegistrationForm()

    return render(
        request,
        'core/register_donor.html',
        {'form': form}
    )


def register_volunteer(request):
    if request.method == 'POST':
        form = VolunteerRegistrationForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']

            if User.objects.filter(username=username).exists():
                form.add_error(
                    'username',
                    'This username is already taken.'
                )
            else:
                with transaction.atomic():
                    user = User.objects.create_user(
                        username=username,
                        password=form.cleaned_data['password']
                    )

                    VolunteerProfile.objects.create(
                        user=user,
                        full_name=form.cleaned_data['full_name'].strip(),
                        phone=form.cleaned_data['phone'].strip(),
                        city=form.cleaned_data['city'].strip(),
                    )

                messages.success(
                    request,
                    'Volunteer registration successful! Please log in.'
                )
                return redirect('donor_login')
    else:
        form = VolunteerRegistrationForm()

    return render(
        request,
        'core/register_volunteer.html',
        {'form': form}
    )


def donor_login(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            if VolunteerProfile.objects.filter(user=user).exists():
                login(request, user)
                return redirect('volunteer_dashboard')

            elif DonorProfile.objects.filter(user=user).exists():
                login(request, user)
                return redirect('search_donors')

            else:
                messages.error(
                    request,
                    'No donor or volunteer profile found for this account.'
                )
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'core/login.html')


def donor_logout(request):
    if request.method == 'POST':
        logout(request)
        messages.success(request, 'You have logged out successfully.')
        return redirect('donor_login')

    return redirect('search_donors')


@login_required
@require_POST
def update_availability(request):
    try:
        donor = request.user.donorprofile
    except DonorProfile.DoesNotExist:
        messages.error(request, 'Donor profile not found.')
        return redirect('search_donors')

    donor.is_available = not donor.is_available
    donor.save(update_fields=['is_available'])

    messages.success(request, 'Availability updated successfully!')
    return redirect('search_donors')


@login_required
def edit_profile(request):
    try:
        donor = DonorProfile.objects.get(user=request.user)
    except DonorProfile.DoesNotExist:
        messages.error(request, 'Donor profile not found.')
        return redirect('search_donors')

    if request.method == 'POST':
        form = DonorProfileForm(request.POST, instance=donor)

        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('search_donors')

        messages.error(
            request,
            'Profile was not updated. Please check the form.'
        )
    else:
        form = DonorProfileForm(instance=donor)

    return render(
        request,
        'core/edit_profile.html',
        {'form': form}
    )


@login_required
def volunteer_dashboard(request):
    return render(request, 'core/volunteer_dashboard.html')


@login_required
def donation_history(request):
    try:
        donor = DonorProfile.objects.get(user=request.user)
    except DonorProfile.DoesNotExist:
        messages.error(
            request,
            'Only registered donors can view donation history.'
        )
        return redirect('search_donors')

    donations = DonationHistory.objects.filter(
        donor=donor
    ).order_by('-donation_date', '-created_at')

    context = {
        'donor': donor,
        'donations': donations,
        'total_donations': donations.count(),
        'total_units': sum(
            donation.units_donated for donation in donations
        ),
    }

    return render(
        request,
        'core/donation_history.html',
        context
    )


@login_required
def create_blood_request(request):
    if request.method == 'POST':
        form = BloodRequestForm(request.POST)

        if form.is_valid():
            blood_request = form.save(commit=False)
            blood_request.requester = request.user
            blood_request.save()

            matching_donors = DonorProfile.objects.filter(
                blood_group=blood_request.blood_group,
                city__iexact=blood_request.city,
                is_available=True,
            ).exclude(
                user=request.user
            ).select_related('user')

            for donor in matching_donors:
                donor_email = donor.user.email

                if donor_email:
                    subject = 'New Blood Request - BloodBridge'

                    email_message = (
                        f"Hello {donor.full_name or donor.user.username},\n\n"
                        f"A new blood request matching your profile has been "
                        f"created on BloodBridge.\n\n"
                        f"Blood Group: {blood_request.blood_group}\n"
                        f"City: {blood_request.city}\n"
                        f"Hospital: {blood_request.hospital_name}\n"
                        f"Units Needed: {blood_request.units_needed}\n"
                        f"Urgency: {blood_request.get_urgency_display()}\n\n"
                        f"Please log in to BloodBridge to view the request.\n\n"
                        f"Thank you,\nBloodBridge Team"
                    )

                    send_notification_email(
                        subject,
                        email_message,
                        donor_email
                    )

            messages.success(
                request,
                'Blood request submitted successfully!'
            )
            return redirect('search_donors')
    else:
        form = BloodRequestForm()

    return render(
        request,
        'core/create_blood_request.html',
        {'form': form}
    )


@login_required
def my_blood_requests(request):
    user_requests = BloodRequest.objects.filter(
        requester=request.user
    )

    if request.method == 'POST':
        request_id = request.POST.get('request_id')

        blood_request = user_requests.filter(
            id=request_id,
            status='pending'
        ).first()

        if blood_request:
            blood_request.status = 'cancelled'
            blood_request.save(update_fields=['status'])
            messages.success(
                request,
                'Blood request cancelled successfully!'
            )
        else:
            messages.error(
                request,
                'Request cannot be cancelled.'
            )

        return redirect('my_blood_requests')

    context = {
        'blood_requests': user_requests.order_by('-created_at'),
        'total_requests': user_requests.count(),
        'pending_count': user_requests.filter(status='pending').count(),
        'accepted_count': user_requests.filter(status='accepted').count(),
        'completed_count': user_requests.filter(status='completed').count(),
        'cancelled_count': user_requests.filter(status='cancelled').count(),
    }

    return render(
        request,
        'core/my_blood_requests.html',
        context
    )


@login_required
def incoming_blood_requests(request):
    try:
        donor = DonorProfile.objects.get(user=request.user)
    except DonorProfile.DoesNotExist:
        messages.error(
            request,
            'Only registered donors can view incoming requests.'
        )
        return redirect('search_donors')

    incoming_requests = BloodRequest.objects.filter(
        blood_group=donor.blood_group,
        city__iexact=donor.city,
        status='pending',
    ).exclude(
        requester=request.user
    ).exclude(
        rejected_by=request.user
    ).order_by('-created_at')

    return render(
        request,
        'core/incoming_blood_requests.html',
        {'incoming_requests': incoming_requests}
    )


@login_required
@require_POST
def accept_blood_request(request, request_id):
    try:
        donor = DonorProfile.objects.get(user=request.user)
    except DonorProfile.DoesNotExist:
        messages.error(
            request,
            'Only registered donors can accept requests.'
        )
        return redirect('search_donors')

    with transaction.atomic():
        blood_request = BloodRequest.objects.select_for_update().filter(
            id=request_id,
            blood_group=donor.blood_group,
            city__iexact=donor.city,
            status='pending',
        ).exclude(
            requester=request.user
        ).exclude(
            rejected_by=request.user
        ).first()

        if blood_request is None:
            messages.error(
                request,
                'This request is no longer available.'
            )
            return redirect('incoming_blood_requests')

        if not donor.is_available:
            messages.error(
                request,
                'Please mark yourself available before accepting a request.'
            )
            return redirect('incoming_blood_requests')

        blood_request.accepted_by = request.user
        blood_request.status = 'accepted'
        blood_request.save(update_fields=['accepted_by', 'status'])

        donor.is_available = False
        donor.save(update_fields=['is_available'])

    requester_email = blood_request.requester.email

    if requester_email:
        subject = 'Your Blood Request Has Been Accepted - BloodBridge'

        email_message = (
            f"Hello {blood_request.requester.username},\n\n"
            f"Good news! A donor has accepted your blood request.\n\n"
            f"Blood Group: {blood_request.blood_group}\n"
            f"City: {blood_request.city}\n"
            f"Hospital: {blood_request.hospital_name}\n"
            f"Donor Name: {donor.full_name or request.user.username}\n"
            f"Donor Phone: {donor.phone}\n\n"
            f"Please log in to BloodBridge to view the request details.\n\n"
            f"Thank you,\nBloodBridge Team"
        )

        send_notification_email(
            subject,
            email_message,
            requester_email
        )

    messages.success(request, 'Blood request accepted successfully!')
    return redirect('incoming_blood_requests')


@login_required
@require_POST
def reject_blood_request(request, request_id):
    try:
        donor = DonorProfile.objects.get(user=request.user)
    except DonorProfile.DoesNotExist:
        messages.error(
            request,
            'Only registered donors can reject requests.'
        )
        return redirect('search_donors')

    blood_request = BloodRequest.objects.filter(
        id=request_id,
        blood_group=donor.blood_group,
        city__iexact=donor.city,
        status='pending',
    ).exclude(
        requester=request.user
    ).first()

    if blood_request is None:
        messages.error(
            request,
            'This request is no longer available.'
        )
        return redirect('incoming_blood_requests')

    blood_request.rejected_by.add(request.user)

    messages.success(
        request,
        'Blood request rejected successfully!'
    )

    return redirect('incoming_blood_requests')


@login_required
def complete_blood_request(request, request_id):
    if request.method != 'POST':
        return redirect('my_blood_requests')

    blood_request = BloodRequest.objects.filter(
        id=request_id,
        requester=request.user,
        status='accepted'
    ).first()

    if blood_request:
        blood_request.status = 'completed'
        blood_request.save(update_fields=['status'])

        messages.success(
            request,
            'Blood request marked as completed successfully!'
        )
    else:
        messages.error(
            request,
            'Request cannot be marked as completed.'
        )

    return redirect('my_blood_requests')











