from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from events.models import Category, Venue, Event
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Populate database with sample data'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Create categories
        categories_data = [
            {'name': 'Concert', 'slug': 'concert', 'description': 'Live music performances'},
            {'name': 'Festival', 'slug': 'festival', 'description': 'Music and cultural festivals'},
            {'name': 'Sports', 'slug': 'sports', 'description': 'Sporting events and competitions'},
        ]
        
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )
            if created:
                self.stdout.write(f'Created category: {category.name}')
        
        # Create venues
        venues_data = [
            {
                'name': 'Madison Square Garden',
                'address': '4 Pennsylvania Plaza',
                'city': 'New York',
                'state': 'NY',
                'zip_code': '10001',
                'capacity': 20000
            },
            {
                'name': 'Hollywood Bowl',
                'address': '2301 Highland Ave',
                'city': 'Los Angeles',
                'state': 'CA',
                'zip_code': '90068',
                'capacity': 17500
            },
            {
                'name': 'Red Rocks Amphitheatre',
                'address': '18300 W Alameda Pkwy',
                'city': 'Morrison',
                'state': 'CO',
                'zip_code': '80465',
                'capacity': 9525
            },
            {
                'name': 'Fenway Park',
                'address': '4 Yawkey Way',
                'city': 'Boston',
                'state': 'MA',
                'zip_code': '02215',
                'capacity': 37755
            },
        ]
        
        for venue_data in venues_data:
            venue, created = Venue.objects.get_or_create(
                name=venue_data['name'],
                defaults=venue_data
            )
            if created:
                self.stdout.write(f'Created venue: {venue.name}')
        
        # Create events
        concert_category = Category.objects.get(slug='concert')
        festival_category = Category.objects.get(slug='festival')
        sports_category = Category.objects.get(slug='sports')
        
        msg = Venue.objects.get(name='Madison Square Garden')
        hollywood = Venue.objects.get(name='Hollywood Bowl')
        red_rocks = Venue.objects.get(name='Red Rocks Amphitheatre')
        fenway = Venue.objects.get(name='Fenway Park')
        
        events_data = [
            {
                'title': 'Live Concert',
                'description': 'An amazing live music performance featuring top artists.',
                'category': concert_category,
                'venue': msg,
                'date': timezone.now() + timedelta(days=5),
                'price': 40.00
            },
            {
                'title': 'Summer Music Festival',
                'description': 'A three-day music festival with multiple stages and artists.',
                'category': festival_category,
                'venue': hollywood,
                'date': timezone.now() + timedelta(days=12),
                'price': 150.00
            },
            {
                'title': 'Championship Game',
                'description': 'The ultimate sporting event of the season.',
                'category': sports_category,
                'venue': fenway,
                'date': timezone.now() + timedelta(days=20),
                'price': 75.00
            },
            {
                'title': 'Rock Concert',
                'description': 'High-energy rock performance under the stars.',
                'category': concert_category,
                'venue': red_rocks,
                'date': timezone.now() + timedelta(days=15),
                'price': 65.00
            },
            {
                'title': 'Jazz Festival',
                'description': 'Smooth jazz performances by renowned artists.',
                'category': festival_category,
                'venue': hollywood,
                'date': timezone.now() + timedelta(days=30),
                'price': 85.00
            },
            {
                'title': 'Basketball Finals',
                'description': 'The championship basketball game of the year.',
                'category': sports_category,
                'venue': msg,
                'date': timezone.now() + timedelta(days=25),
                'price': 120.00
            },
        ]
        
        for event_data in events_data:
            event, created = Event.objects.get_or_create(
                title=event_data['title'],
                defaults=event_data
            )
            if created:
                self.stdout.write(f'Created event: {event.title}')
        
        self.stdout.write(self.style.SUCCESS('Successfully populated database with sample data!'))
