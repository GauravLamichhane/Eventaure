from django.db import models
from django.contrib import admin
from django.db.models import Count
from .models import Event, Registration



admin.site.site_header = "Event Management Admin"
admin.site.site_title = "EMS Admin"
admin.site.index_title = "Dashboard"


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = [
        "title", "event_type", "organizer", "is_published",
        "capacity", "registered_count", "waitlist_capacity", "waitlisted_count"
    ]
    search_fields = ["title", "organizer__email"]

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            registered_count_value=Count(
                "event_registrations",
                filter=models.Q(event_registrations__status="registered")
            ),
            waitlisted_count_value=Count(
                "event_registrations",
                filter=models.Q(event_registrations__status="waitlisted")
            ),
        )

    def registered_count(self, obj):
        capacity = f"/{obj.capacity}" if obj.capacity else ""
        return f"{obj.registered_count_value}{capacity}"
    registered_count.short_description = "Registered"

    def waitlisted_count(self, obj):
        waitlist_capacity = f"/{obj.waitlist_capacity}" if obj.waitlist_capacity else ""
        return f"{obj.waitlisted_count_value}{waitlist_capacity}"
    waitlisted_count.short_description = "Waitlisted"

@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ["event", "attendee", "status", "registered_at"]
    list_filter = ["status"]
    search_fields = ["attendee__email", "event__title"]