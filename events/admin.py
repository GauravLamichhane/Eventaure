from django.contrib import admin
from django.db.models import Count
from .models import Event, Registration



admin.site.site_header = "Event Management Admin"
admin.site.site_title = "EMS Admin"
admin.site.index_title = "Dashboard"


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
  list_display = ["title","description","event_type","organizer"]
  search_fields = ["title", "organizer"]



@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ["event", "attendee_count"]

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            attendee_count_value=Count("event__event_registrations")
        )

    def attendee_count(self, obj):
        return obj.attendee_count_value