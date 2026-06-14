from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import EventViewSet, RegistrationViewSet

router = DefaultRouter()
router.register(r"events", EventViewSet, basename="events")
router.register(r"registrations", RegistrationViewSet, basename="registration")

urlpatterns = router.urls

