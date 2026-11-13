from django.urls import path
from .views import PublicGhats, PublicSlots, MyBookings, CreateBooking, PoliceCheckIn, MyComplaints, SensorIngest, AdminOverview

urlpatterns = [
    path("ghats/", PublicGhats.as_view()),
    path("slots/", PublicSlots.as_view()),
    path("bookings/", MyBookings.as_view()),
    path("bookings/create/", CreateBooking.as_view()),
    path("police/check-in/", PoliceCheckIn.as_view()),
    path("complaints/", MyComplaints.as_view()),
    path("sensors/water/", SensorIngest.as_view()),
    path("admin/overview/", AdminOverview.as_view()),
]
