import django_filters
from .models import Event


class EventFilter(django_filters.FilterSet):
  event_type = django_filters.CharFilter(field_name="event_type",lookup_expr="iexact")
  is_published = django_filters.BooleanFilter(field_name="is_published")
  start_after = django_filters.DateTimeFilter(
    field_name="start_datetime", lookup_expr="gte"
  )
  start_before = django_filters.DateTimeFilter(
    field_name="start_datetime", lookup_expr="lte"
  )
  location = django_filters.CharFilter(
    field_name="location", lookup_expr="icontains"
  )
  organizer = django_filters.CharFilter(field_name="organizer__email", lookup_expr='iexact')

  class Meta:
    model = Event
    fields = ['event_type', 'is_published', 'start_after', 'start_before', 'location', 'organizer']