from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from notifications.views import create_notification


def send_booking_confirmation_email(booking):
    """Send booking confirmation email to user"""
    try:
        # Get user's notification preferences
        preferences = getattr(booking.user, 'notification_preferences', None)
        if preferences and not preferences.email_notifications:
            return False
        
        subject = f'Booking Confirmation - {booking.event.title}'
        
        # Render HTML email
        html_message = render_to_string('emails/booking_confirmation.html', {
            'booking': booking,
        })
        
        # Render plain text email
        plain_message = render_to_string('emails/booking_confirmation.txt', {
            'booking': booking,
        })
        
        # Send email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking.user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        return True
        
    except Exception as e:
        print(f"Error sending booking confirmation email: {e}")
        return False


def send_booking_cancellation_email(booking):
    """Send booking cancellation email to user"""
    try:
        # Get user's notification preferences
        preferences = getattr(booking.user, 'notification_preferences', None)
        if preferences and not preferences.email_notifications:
            return False
        
        subject = f'Booking Cancelled - {booking.event.title}'
        
        message = f"""
Hi {booking.user.first_name or booking.user.username},

Your booking for {booking.event.title} has been cancelled.

Booking Details:
- Event: {booking.event.title}
- Date: {booking.event.date.strftime('%B %d, %Y at %I:%M %p')}
- Booking Reference: {booking.booking_reference}
- Amount: ${booking.total_amount}

If you have any questions, please contact our support team.

Best regards,
The EventSphere Team
        """
        
        send_mail(
            subject=subject,
            message=message.strip(),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking.user.email],
            fail_silently=False,
        )
        
        return True
        
    except Exception as e:
        print(f"Error sending booking cancellation email: {e}")
        return False


def send_event_reminder_email(booking):
    """Send event reminder email to user"""
    try:
        # Get user's notification preferences
        preferences = getattr(booking.user, 'notification_preferences', None)
        if preferences and not preferences.event_reminders:
            return False
        
        subject = f'Event Reminder - {booking.event.title} Tomorrow!'
        
        message = f"""
Hi {booking.user.first_name or booking.user.username},

This is a friendly reminder that your event is tomorrow!

Event Details:
- Event: {booking.event.title}
- Venue: {booking.event.venue.name}
- Date: {booking.event.date.strftime('%B %d, %Y at %I:%M %p')}
- Tickets: {booking.quantity}
- Booking Reference: {booking.booking_reference}

Don't forget to bring:
- This confirmation email
- A valid ID
- Your booking reference: {booking.booking_reference}

We hope you have an amazing time!

Best regards,
The EventSphere Team
        """
        
        send_mail(
            subject=subject,
            message=message.strip(),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking.user.email],
            fail_silently=False,
        )
        
        # Create notification
        create_notification(
            user=booking.user,
            title='Event Reminder',
            message=f'Your event {booking.event.title} is tomorrow!',
            notification_type='event_reminder',
            event=booking.event,
            booking=booking
        )
        
        return True
        
    except Exception as e:
        print(f"Error sending event reminder email: {e}")
        return False
