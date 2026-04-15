from django.db import models
from django.conf import settings
from django.db.models import Q

class Booking(models.Model):
    class Status(models.TextChoices):
        CONFIRMED = 'confirmed', 'Confirmed'
        CANCELLED = 'cancelled', 'Cancelled'
        COMPLETED = 'completed', 'Completed'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    session = models.ForeignKey(
        'sessions_app.Session',
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.CONFIRMED
    )
    booked_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-booked_at']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'session'],
                condition=Q(status__in=['confirmed', 'completed']),
                name='unique_active_booking_per_user_session'
            )
        ]

    def __str__(self):
        return f'{self.user.email} → {self.session.title}'