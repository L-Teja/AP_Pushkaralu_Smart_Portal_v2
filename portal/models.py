import secrets
from django.conf import settings
from django.db import models
from django.utils import timezone

class Profile(models.Model):
    ROLES = [(r, r.replace("_", " ").title()) for r in [
        "visitor", "police", "sanitation", "food_safety", "medical",
        "transport", "vendor", "admin"
    ]]
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=24, choices=ROLES, default="visitor")
    department_code = models.CharField(max_length=40, blank=True)

class Ghat(models.Model):
    name = models.CharField(max_length=120)
    district = models.CharField(max_length=100)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} — {self.district}"

class Slot(models.Model):
    ghat = models.ForeignKey(Ghat, on_delete=models.PROTECT)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    capacity = models.PositiveIntegerField()
    booked_count = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("ghat", "date", "start_time", "end_time")
        ordering = ("date", "start_time")

class Booking(models.Model):
    STATUS = [("booked", "Booked"), ("checked_in", "Checked in"), ("cancelled", "Cancelled")]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    slot = models.ForeignKey(Slot, on_delete=models.PROTECT)
    booking_number = models.CharField(max_length=24, unique=True, editable=False)
    qr_token = models.CharField(max_length=64, unique=True, editable=False)
    people_count = models.PositiveSmallIntegerField(default=1)
    status = models.CharField(max_length=16, choices=STATUS, default="booked")
    checked_in_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.booking_number:
            self.booking_number = "AP" + secrets.token_hex(5).upper()
        if not self.qr_token:
            self.qr_token = secrets.token_urlsafe(32)
        super().save(*args, **kwargs)

class Complaint(models.Model):
    DEPARTMENTS = [("sanitation", "Sanitation"), ("food_safety", "Food Safety"),
                   ("medical", "Medical"), ("transport", "Transport")]
    STATUS = [("open", "Open"), ("assigned", "Assigned"), ("resolved", "Resolved")]
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    department = models.CharField(max_length=24, choices=DEPARTMENTS)
    subject = models.CharField(max_length=160)
    description = models.TextField()
    status = models.CharField(max_length=16, choices=STATUS, default="open")
    created_at = models.DateTimeField(auto_now_add=True)

class WaterReading(models.Model):
    ghat = models.ForeignKey(Ghat, on_delete=models.PROTECT)
    sensor_id = models.CharField(max_length=80, db_index=True)
    level_cm = models.FloatField()
    warning_threshold_cm = models.FloatField()
    danger_threshold_cm = models.FloatField()
    received_at = models.DateTimeField(default=timezone.now)
    verified = models.BooleanField(default=False)

    @property
    def alert_level(self):
        if self.level_cm >= self.danger_threshold_cm:
            return "danger"
        if self.level_cm >= self.warning_threshold_cm:
            return "warning"
        return "normal"

class AuditLog(models.Model):
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    action = models.CharField(max_length=100)
    object_type = models.CharField(max_length=80)
    object_id = models.CharField(max_length=80)
    created_at = models.DateTimeField(auto_now_add=True)
