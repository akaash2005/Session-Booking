from django.contrib import admin
from .models import Session

@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ['title', 'creator', 'price', 'date', 'status', 'spots_left']
    list_filter = ['status', 'date']
    search_fields = ['title', 'creator__email']