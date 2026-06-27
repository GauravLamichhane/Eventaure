from rest_framework import serializers
from .models import Event, Registration


class EventSerializer(serializers.ModelSerializer):
  organizer_name = serializers.SerializerMethodField()

  def get_organizer_name(self, obj):
    return f"{obj.organizer.first_name} {obj.organizer.last_name}".strip()

  def validate_title(self, value):
    if len(value) < 5:
      raise serializers.ValidationError("Title must be at least 5 characters long.")
    return value
  
  def validate_image(self, value):
    max_size = 5 * 1024 * 1024
    
    if value.size > max_size:
      raise serializers.ValidationError(
        "Image size cannot exceed 5MB"
      )
    
    allowed_types = [
      "image/jpeg",
      "image/png",
      "image/webp"
    ]

    if value.content_type not in allowed_types:
      raise serializers.ValidationError(
        "Only JPG, PNG, WEBP allowed"
      )
    return value

  def validate_capacity(self, value):
    if value is not None and value < 1:
      raise serializers.ValidationError("Capacity must be at least 1.")
    return value
  
  def validate(self, attrs):
    start_datetime = attrs.get("start_datetime", getattr(self.instance, "start_datetime", None))
    end_datetime = attrs.get("end_datetime", getattr(self.instance, "end_datetime", None))
    capacity = attrs.get("capacity", getattr(self.instance, "capacity", None))
    waitlist_capacity = attrs.get("waitlist_capacity", getattr(self.instance, "waitlist_capacity", None))

    if start_datetime and end_datetime and end_datetime <= start_datetime:
      raise serializers.ValidationError({"end_datetime": "End date and time must be after the start date and time."})
    
    event_type = attrs.get("event_type", getattr(self.instance, "event_type", None))
    location = attrs.get("location", getattr(self.instance, "location", None))
    meeting_url = attrs.get("meeting_url", getattr(self.instance, "meeting_url", None))

    if event_type == "physical":
      if not location:
            raise serializers.ValidationError({"location":"Physical event must have a location."})
      if meeting_url:
        raise serializers.ValidationError({"meeting_url":"Physical event don't have meeting url"})
      
    if event_type == "online":
      if not meeting_url:
        raise serializers.ValidationError({"meeting_url":"Online event must have a meeting url"})
      if location:
        raise serializers.ValidationError({"location":"Online events don't have a physical location."})
    
    if event_type == "hybrid":
      if not location:
        raise serializers.ValidationError({"location":"Hybrid event must have a physical location."})
      if not meeting_url:
        raise serializers.ValidationError({"meeting_url":"Hybrid event must have a meeting url."})
    
    if waitlist_capacity is not None and capacity is not None:
      if waitlist_capacity > capacity:
        raise serializers.ValidationError({
          "waitlist_capacity": "Waitlist capacity cannot exceed event capacity."
        })

    return attrs
  
  class Meta:
    model = Event
    fields = [
            "id",
            "title",
            "image",
            "description",
            "event_type",
            "location",
            "meeting_url",
            "meeting_platform",
            "start_datetime",
            "end_datetime",
            "capacity",
            "waitlist_capacity",
            "is_published",
            "organizer",
            "organizer_name",
            "created_at",
            "updated_at",
        ]
    read_only_fields = [
      "id",
      "organizer",
      "organizer_name",
      "created_at",
      "updated_at",
      "is_published"
    ]


class RegistrationSerializer(serializers.ModelSerializer):
  attendee_email = serializers.EmailField(source="attendee.email", read_only = True)
  event_title = serializers.CharField(source = "event.title", read_only = True)

  class Meta:
    model = Registration
    fields = ["id","event","event_title", "attendee_email","status","registered_at"]
    read_only_fields = ["id","attendee_email","event_title","status","registered_at"]

  def validate(self, attrs):
    event = attrs.get("event") #This comes from request data (serializer input)
    attendee = self.context["request"].user #this comes from auth system self.context -> extra data passed to the serializer
    """
    self.context	extra data passed to serializer
    self.context["request"]	the HTTP request object
    self.context["request"].user	authenticated user
    """

    #one can't register for unpublished event
    if not event.is_published:
      raise serializers.ValidationError("This event is not published yet.")
    
    if event.organizer == attendee:
      raise serializers.ValidationError("Organizers cannot register to their own event.")
    
    existing = Registration.objects.filter(event = event, attendee = attendee).first()
    if existing:
      if existing.status in ["registered","waitlisted"]:
        raise serializers.ValidationError("You are already registered or waitlisted for this event.")
    
    return attrs