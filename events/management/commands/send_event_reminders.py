from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from events.models import Booking
from events.email_utils import send_event_reminder_email


class Command(BaseCommand):
    help = 'Send event reminder emails to users with bookings for events happening tomorrow'

    def handle(self, *args, **options):
        # Get tomorrow's date
        tomorrow = timezone.now() + timedelta(days=1)
        tomorrow_start = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow_end = tomorrow.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        # Get all confirmed bookings for events happening tomorrow
        bookings = Booking.objects.filter(
            status='confirmed',
            event__date__gte=tomorrow_start,
            event__date__lte=tomorrow_end,
            event__is_active=True
        ).select_related('user', 'event', 'event__venue')
        
        sent_count = 0
        failed_count = 0
        
        for booking in bookings:
            try:
                if send_event_reminder_email(booking):
                    sent_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Sent reminder to {booking.user.email} for {booking.event.title}'
                        )
                    )
                else:
                    failed_count += 1
                    self.stdout.write(
                        self.style.WARNING(
                            f'Skipped reminder for {booking.user.email} (preferences disabled)'
                        )
                    )
            except Exception as e:
                failed_count += 1
                self.stdout.write(
                    self.style.ERROR(
                        f'Failed to send reminder to {booking.user.email}: {str(e)}'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Event reminder task completed. Sent: {sent_count}, Failed/Skipped: {failed_count}'
            )
        )
