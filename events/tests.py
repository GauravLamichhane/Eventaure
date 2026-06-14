from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIRequestFactory, force_authenticate

from users.models import CustomUser

from .models import Event
from .serializers import EventSerializer
from .views import EventViewSet


class EventSerializerTests(TestCase):
	def setUp(self):
		self.user = CustomUser.objects.create_user(
			email="organizer@example.com",
			password="testpassword123",
			first_name="Ada",
			last_name="Lovelace",
		)

	def test_create_payload_does_not_require_read_only_fields(self):
		serializer = EventSerializer(
			data={
				"title": "Annual Tech Meetup",
				"description": "A community event for developers",
				"location": "Main Hall",
				"start_datetime": timezone.now() + timezone.timedelta(days=1),
				"end_datetime": timezone.now() + timezone.timedelta(days=1, hours=2),
				"capacity": 200,
				"is_published": True,
			}
		)

		self.assertTrue(serializer.is_valid(), serializer.errors)

	def test_rejects_end_datetime_before_start_datetime(self):
		serializer = EventSerializer(
			data={
				"title": "Annual Tech Meetup",
				"description": "A community event for developers",
				"location": "Main Hall",
				"start_datetime": timezone.now() + timezone.timedelta(days=1),
				"end_datetime": timezone.now() + timezone.timedelta(hours=1),
				"capacity": 200,
				"is_published": True,
			}
		)

		self.assertFalse(serializer.is_valid())
		self.assertIn("end_datetime", serializer.errors)


class EventViewSetTests(TestCase):
	def setUp(self):
		self.factory = APIRequestFactory()
		self.user = CustomUser.objects.create_user(
			email="viewer@example.com",
			password="testpassword123",
			first_name="Viewer",
			last_name="User",
		)
		self.other_user = CustomUser.objects.create_user(
			email="organizer@example.com",
			password="testpassword123",
			first_name="Organizer",
			last_name="User",
		)
		Event.objects.create(
			title="Public Event",
			description="Visible to all authenticated users",
			event_type="physical",
			location="Main Hall",
			start_datetime=timezone.now() + timezone.timedelta(days=1),
			end_datetime=timezone.now() + timezone.timedelta(days=1, hours=2),
			organizer=self.other_user,
			is_published=True,
		)
		Event.objects.create(
			title="My Event",
			description="Created by the viewer",
			event_type="physical",
			location="Room 2",
			start_datetime=timezone.now() + timezone.timedelta(days=2),
			end_datetime=timezone.now() + timezone.timedelta(days=2, hours=2),
			organizer=self.user,
			is_published=True,
		)

	def test_list_returns_all_events_for_authenticated_user(self):
		request = self.factory.get("/api/events/")
		force_authenticate(request, user=self.user)

		response = EventViewSet.as_view({"get": "list"})(request)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(len(response.data), 2)
		self.assertCountEqual(
			[event["title"] for event in response.data],
			["Public Event", "My Event"],
		)
