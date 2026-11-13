from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import DonorProfile, BloodRequest
from .serializers import DonorSerializer, BloodRequestSerializer


class DonorListAPIView(generics.ListAPIView):
    serializer_class = DonorSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = DonorProfile.objects.filter(
            is_available=True
        )

        blood_group = self.request.query_params.get('blood_group')
        city = self.request.query_params.get('city')

        if blood_group:
            queryset = queryset.filter(
                blood_group=blood_group
            )

        if city:
            queryset = queryset.filter(
                city__iexact=city
            )

        return queryset


class BloodRequestListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = BloodRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return BloodRequest.objects.filter(
            requester=self.request.user
        ).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(requester=self.request.user)


class BloodRequestDetailAPIView(generics.RetrieveAPIView):
    serializer_class = BloodRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return BloodRequest.objects.filter(
            requester=self.request.user
        )
    