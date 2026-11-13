from django.db import transaction
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Ghat, Slot, Booking, Complaint, WaterReading, AuditLog
from .serializers import (GhatSerializer, SlotSerializer, BookingSerializer,
                          BookingCreateSerializer, ComplaintSerializer, WaterReadingSerializer)
from .permissions import IsPoliceOrAdmin, IsAdminRole

class PublicGhats(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = GhatSerializer
    queryset = Ghat.objects.filter(active=True)

class PublicSlots(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = SlotSerializer
    def get_queryset(self):
        qs = Slot.objects.filter(active=True, date__range=("2027-06-26", "2027-07-07"))
        ghat_id = self.request.query_params.get("ghat")
        day = self.request.query_params.get("date")
        if ghat_id: qs = qs.filter(ghat_id=ghat_id)
        if day: qs = qs.filter(date=day)
        return qs.select_related("ghat")

class MyBookings(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BookingSerializer
    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user).select_related("slot", "slot__ghat")

class CreateBooking(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        data = BookingCreateSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        with transaction.atomic():
            slot = Slot.objects.select_for_update().get(pk=data.validated_data["slot_id"], active=True)
            count = data.validated_data["people_count"]
            if slot.date < timezone.localdate() or slot.date.isoformat() < "2027-06-26" or slot.date.isoformat() > "2027-07-07":
                return Response({"detail": "This slot is outside the configured festival dates."}, status=400)
            if slot.booked_count + count > slot.capacity:
                return Response({"detail": "This time slot is full. Please choose another slot."}, status=409)
            booking = Booking.objects.create(user=request.user, slot=slot, people_count=count)
            slot.booked_count += count
            slot.save(update_fields=["booked_count"])
            AuditLog.objects.create(actor=request.user, action="booking_created",
                                    object_type="Booking", object_id=str(booking.id))
        # Integrate email/SMS provider asynchronously after booking commits.
        return Response(BookingSerializer(booking).data, status=status.HTTP_201_CREATED)

class PoliceCheckIn(APIView):
    permission_classes = [IsAuthenticated, IsPoliceOrAdmin]
    def post(self, request):
        token = request.data.get("qr_token")
        number = request.data.get("booking_number")
        qs = Booking.objects.select_related("slot", "slot__ghat")
        booking = qs.filter(qr_token=token).first() if token else qs.filter(booking_number=number).first()
        if not booking:
            return Response({"detail": "Booking not found."}, status=404)
        if booking.status != "booked":
            return Response({"detail": "Ticket is already used or cancelled."}, status=409)
        booking.status = "checked_in"
        booking.checked_in_at = timezone.now()
        booking.save(update_fields=["status", "checked_in_at"])
        AuditLog.objects.create(actor=request.user, action="checked_in",
                                object_type="Booking", object_id=str(booking.id))
        # Return minimum necessary data; do not return phone/email/address.
        return Response({"status": "checked_in", "booking_number": booking.booking_number,
                         "ghat": booking.slot.ghat.name, "date": booking.slot.date,
                         "slot_start": booking.slot.start_time, "slot_end": booking.slot.end_time,
                         "people_count": booking.people_count})

class MyComplaints(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ComplaintSerializer
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or (hasattr(user, "profile") and user.profile.role in
                                 ("admin", "sanitation", "food_safety", "medical", "transport")):
            role = getattr(getattr(user, "profile", None), "role", "admin")
            if role == "admin": return Complaint.objects.all()
            return Complaint.objects.filter(department=role)
        return Complaint.objects.filter(created_by=user)
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class SensorIngest(APIView):
    # Replace this with signed device credentials/mTLS and network allow-listing.
    # Do not expose this endpoint publicly without device authentication.
    permission_classes = [IsAdminRole]
    def post(self, request):
        serializer = WaterReadingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reading = serializer.save()
        AuditLog.objects.create(actor=request.user, action="water_reading_ingested",
                                object_type="WaterReading", object_id=str(reading.id))
        return Response(WaterReadingSerializer(reading).data, status=201)

class AdminOverview(APIView):
    permission_classes = [IsAdminRole]
    def get(self, request):
        return Response({
            "bookings": Booking.objects.count(),
            "checked_in": Booking.objects.filter(status="checked_in").count(),
            "open_complaints": Complaint.objects.exclude(status="resolved").count(),
            "active_ghats": Ghat.objects.filter(active=True).count(),
            "latest_water_readings": WaterReadingSerializer(
                WaterReading.objects.select_related("ghat").order_by("-received_at")[:10], many=True
            ).data,
        })
