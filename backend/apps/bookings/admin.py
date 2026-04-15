from django.contrib import admin
from .models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['user', 'session', 'status', 'booked_at']
    list_filter = ['status']
    search_fields = ['user__email', 'session__title']