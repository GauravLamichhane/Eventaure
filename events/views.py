from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.exceptions import PermissionDenied
from .models import Event, Registration
from events.serializers import EventSerializer, RegistrationSerializer
from .filters import EventFilter

class EventViewSet(ModelViewSet):
  serializer_class = EventSerializer
  permission_classes = [IsAuthenticated]
  filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
  filterset_class = EventFilter
  search_fields = ['title', 'description', 'location']
  ordering_fields = ['start_datetime', 'created_at', 'capacity']
  ordering = ['-created_at']

  def get_queryset(self):
    return Event.objects.all()
  
  def perform_create(self, serializer):
    serializer.save(organizer = self.request.user)

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
    serializer.save(attendee = self.request.user)
  

  def partial_update(self, request, *args, **kwargs):
    
    instance = self.get_object()
    if instance.attendee != request.user:
      raise PermissionDenied("You can only cancel your own registration.")
    
    if instance.status == "cancelled":
      raise PermissionDenied("Registration is already cancelled.")
    
    instance.status = "cancelled"
    instance.save()
    return Response(RegistrationSerializer(instance).data)
  
  def destroy(self, request, *args, **kwargs):
    instance = self.get_object()

    if instance.event.organizer != request.user:
      raise PermissionDenied("Only the organizer can remove registrations.")
    
    return super().destroy(request, *args, **kwargs)