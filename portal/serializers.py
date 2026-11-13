from rest_framework import serializers
from .models import Ghat, Slot, Booking, Complaint, WaterReading

class GhatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ghat
        fields = ("id", "name", "district", "active")

class SlotSerializer(serializers.ModelSerializer):
    ghat_name = serializers.CharField(source="ghat.name", read_only=True)
    available = serializers.SerializerMethodField()
    class Meta:
        model = Slot
        fields = ("id", "ghat", "ghat_name", "date", "start_time", "end_time",
                  "capacity", "booked_count", "available", "active")
    def get_available(self, obj):
        return max(0, obj.capacity - obj.booked_count)

class BookingSerializer(serializers.ModelSerializer):
    slot = SlotSerializer(read_only=True)
    class Meta:
        model = Booking
        fields = ("id", "booking_number", "qr_token", "people_count", "status", "slot", "created_at")
        read_only_fields = fields

class BookingCreateSerializer(serializers.Serializer):
    slot_id = serializers.IntegerField()
    people_count = serializers.IntegerField(min_value=1, max_value=10)

class ComplaintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complaint
        fields = ("id", "department", "subject", "description", "status", "created_at")
        read_only_fields = ("id", "status", "created_at")

class WaterReadingSerializer(serializers.ModelSerializer):
    alert_level = serializers.CharField(read_only=True)
    class Meta:
        model = WaterReading
        fields = ("id", "ghat", "sensor_id", "level_cm", "warning_threshold_cm",
                  "danger_threshold_cm", "received_at", "verified", "alert_level")
