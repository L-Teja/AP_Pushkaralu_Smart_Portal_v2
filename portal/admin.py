from django.contrib import admin
from .models import Profile, Ghat, Slot, Booking, Complaint, WaterReading, AuditLog
admin.site.register([Profile, Ghat, Slot, Booking, Complaint, WaterReading, AuditLog])
