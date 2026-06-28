from django.db import models
from users.models import CustomUser

class Event(models.Model):
  EVENT_TYPE_CHOICES = [
    ("physical","Physical"),
    ("online","Online"),
    ("hybrid","Hybrid"),
  ]

  title = models.CharField(max_length=255)
  image = models.ImageField(upload_to="events/", blank=True, null=True)
  description = models.TextField(blank=True)
  event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES, default="physical")
  location = models.CharField(max_length=255, blank=True)
  meeting_url = models.URLField(blank=True)
  meeting_platform = models.CharField(max_length=100, blank=True)
  start_datetime = models.DateTimeField()
  end_datetime = models.DateTimeField()
  organizer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="events")
  capacity = models.PositiveIntegerField(null=True, blank=True)
  waitlist_capacity = models.PositiveIntegerField(null=True, blank=True)
  is_published = models.BooleanField(default=False)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  def __str__(self):
    return self.title
  
class Registration(models.Model):
  STATUS_CHOICES = [
    ("registered","Registered"),
    ("cancelled","Cancelled"),
    ("waitlisted","Waitlisted"),
  ]
  event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="event_registrations")
  attendee = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="user_registrations")
  status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="registered")
  registered_at = models.DateTimeField(auto_now_add=True)

 
  class Meta:
      constraints = [
        models.UniqueConstraint(fields=["event", "attendee"], name="unique_event_attendee")
      ]
  def __str__(self):
        return f"{self.attendee.email}"