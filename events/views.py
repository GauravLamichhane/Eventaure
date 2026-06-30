from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.viewsets import ModelViewSet
from rest_framework.exceptions import PermissionDenied
from .models import Event, Registration
from events.serializers import EventSerializer, RegistrationSerializer
from .filters import EventFilter
from .utils import send_waitlist_promotion_email

class EventViewSet(ModelViewSet):
  serializer_class = EventSerializer
  pagination_class = None
  permission_classes = [IsAuthenticatedOrReadOnly]
  filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
  filterset_class = EventFilter
  search_fields = ['title', 'description', 'location']
  ordering_fields = ['start_datetime', 'created_at', 'capacity']
  ordering = ['-created_at']

  def get_queryset(self):
    queryset = Event.objects.all()
    if self.request.query_params.get("mine") == "true":
      queryset = queryset.filter(organizer = self.request.user)
    return queryset
  
  def perform_create(self, serializer):
    serializer.save(organizer = self.request.user)

  def check_organizer(self, instance):
    print(instance.organizer)
    print(self.request.user)
    if instance.organizer != self.request.user:
      raise PermissionDenied("Only the Organizer can perform this action.")
  
  def perform_update(self, serializer):
    self.check_organizer(self.get_object())
    serializer.save()
  
  def perform_destroy(self, instance):
    self.check_organizer(instance)
    instance.delete()
  
  @action(detail=True, methods = ["post"])
  def publish(self, request, pk=None):
    event = self.get_object()
    self.check_organizer(event)

    if event.is_published:
      return Response({"detail":"Event is already published."}, status=400)
    event.is_published = True
    event.save()
    return Response({"detail":"Event published successfully."})
  
  @action(detail=True, methods=["post"])
  def unpublish(self, request, pk = None):
    event = self.get_object()
    self.check_organizer(event)

    if not event.is_published:
      return Response({"detail":"Event is already unpublished."}, status=400)
    event.is_published = False
    event.save()
    return Response({"detail":"Event unpublished successfully."})


"""
DELETE /events/1/
        │
        ▼
destroy()
        │
        ▼
event = self.get_object()
        │
        ▼
event = Event(id=1, organizer=Ram)
        │
        ▼
self.check_organizer(event)
        │
        ▼
instance = event
        │
        ▼
instance.organizer == self.request.user
        │
        ▼
Ram == Ram
        │
        ▼
True
"""


class RegistrationViewSet(ModelViewSet):
  serializer_class = RegistrationSerializer
  permission_classes = [IsAuthenticated]
  http_method_names = ["get", "post", "put", "delete"]

  def get_queryset(self):
      user = self.request.user

      return Registration.objects.filter(
          Q(attendee=user) |
          Q(event__organizer=user)
      ).select_related(
          "event",
          "attendee"
      )
  
  def perform_create(self, serializer):
    event = serializer.validated_data["event"]
    attendee = self.request.user

    #determine status based on capacity
    if event.capacity is not None:
      active_count = Registration.objects.filter(
        event = event,
        status = "registered"
      ).count()

      if active_count >= event.capacity:
        if event.waitlist_capacity is None:
          raise serializers.ValidationError("This event is full and has no waitlist.")
        
        waitlisted_count = Registration.objects.filter(
          event = event, 
          status = "waitlisted"
        ).count()

        if waitlisted_count >= event.waitlist_capacity:
          raise serializers.ValidationError(
            f"This event is full and the waitlist is also full ({event.waitlist_capacity} spots)."
          )
        serializer.save(attendee = attendee, status = "waitlisted")
        return
    serializer.save(attendee = attendee, status = "registered")
  

  def partial_update(self, request, *args, **kwargs):
    
    instance = self.get_object()
    if instance.attendee != request.user:
      raise PermissionDenied("You can only cancel your own registration.")
    
    if instance.status == "cancelled":
      raise PermissionDenied("Registration is already cancelled.")
    
    instance.status = "cancelled"
    instance.save()

    self._promote_from_waitlist(instance.event)
    return Response(RegistrationSerializer(instance).data)
  
  def _promote_from_waitlist(self, event):
    if event.capacity is None:
      return #no capacity limit, no waitlist needed
    
    active_count = Registration.objects.filter(
      event = event,
      status = "registered"
    ).count()

    if active_count < event.capacity:
      next_in_line = Registration.objects.filter(
        event = event,
        status = "waitlisted"
      ).order_by("registered_at").first() #oldest waitlisted first

      if next_in_line:
        next_in_line.status = "registered"
        next_in_line.save()
        send_waitlist_promotion_email(next_in_line)
        
  
  def destroy(self, request, *args, **kwargs):
    instance = self.get_object()

    if instance.event.organizer != request.user:
      raise PermissionDenied("Only the organizer can remove registrations.")
    
    return super().destroy(request, *args, **kwargs)

