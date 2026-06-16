from django.core.mail import send_mail
from django.conf import settings


def send_waitlist_promotion_email(registration):
  send_mail(
            subject=f"You're in! Your spot for {registration.event.title} is confirmed.",
            message= (f"Hi {registration.attendee.first_name},\n\n"
            f"Good news! A spot opened up for '{registration.event.title}' "
            f"and you've been moved from the waitlist to registered.\n\n"
            f"Event starts at: {registration.event.start_datetime.strftime('%B %d, %Y at %I:%M %p')}\n\n"
            f"See you there!"
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[registration.attendee.email],
  )