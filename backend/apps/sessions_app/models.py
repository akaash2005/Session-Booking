from django.db import models
from django.conf import settings

class Session(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        PUBLISHED = 'published', 'Published'
        CANCELLED = 'cancelled', 'Cancelled'

    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sessions'
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    date = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=60)
    max_participants = models.PositiveIntegerField(default=10)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PUBLISHED
    )
    cover_image = models.ImageField(upload_to='sessions/', blank=True, null=True)
    tags = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def spots_left(self):
        booked = self.bookings.filter(status='confirmed').count()
        return self.max_participants - booked

    @property
    def is_available(self):
        return self.spots_left > 0 and self.status == self.Status.PUBLISHED