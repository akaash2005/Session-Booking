#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.bookings.models import Booking
from apps.accounts.models import User

users = User.objects.all()
print(f"Total users: {users.count()}")

for user in users:
    bookings = Booking.objects.filter(user=user)
    print(f"\nUser: {user.email} (ID: {user.id})")
    print(f"Bookings: {bookings.count()}")
    for booking in bookings:
        print(f"  - Booking ID {booking.id}: Session {booking.session_id}, Status: {booking.status}")
