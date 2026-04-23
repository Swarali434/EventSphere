from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count, Sum
from events.models import Event, UserFavorite, Booking
from notifications.models import Notification
from django.utils import timezone
import calendar
from datetime import datetime, timedelta


@login_required
def dashboard_view(request):
    # Get user's favorite events
    favorites = UserFavorite.objects.filter(user=request.user).select_related('event')[:4]

    # Get upcoming events for calendar view
    today = timezone.now()
    upcoming_events = Event.objects.filter(
        date__gte=today,
        is_active=True
    ).order_by('date')[:10]

    # Search functionality
    query = request.GET.get('q', '')
    search_results = []
    if query:
        search_results = Event.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(venue__name__icontains=query),
            is_active=True
        )[:5]

    # Get user's bookings
    recent_bookings = Booking.objects.filter(user=request.user).order_by('-created_at')[:5]

    # Get user statistics
    total_bookings = Booking.objects.filter(user=request.user).count()
    total_spent = Booking.objects.filter(user=request.user, status='confirmed').aggregate(
        total=Sum('total_amount')
    )['total'] or 0

    # Get unread notifications
    unread_notifications = Notification.objects.filter(user=request.user, is_read=False).count()

    # Get events created by user
    my_events_count = Event.objects.filter(created_by=request.user).count()

    context = {
        'favorites': favorites,
        'upcoming_events': upcoming_events,
        'search_results': search_results,
        'query': query,
        'recent_bookings': recent_bookings,
        'total_bookings': total_bookings,
        'total_spent': total_spent,
        'unread_notifications': unread_notifications,
        'my_events_count': my_events_count,
    }
    return render(request, 'dashboard/dashboard.html', context)


@login_required
def favorites_view(request):
    favorites = UserFavorite.objects.filter(user=request.user).select_related('event')
    context = {
        'favorites': favorites,
    }
    return render(request, 'dashboard/favorites.html', context)


@login_required
def calendar_view(request):
    today = timezone.now()

    # Get current month and year
    month = int(request.GET.get('month', today.month))
    year = int(request.GET.get('year', today.year))

    # Get events for the current month
    events = Event.objects.filter(
        date__year=year,
        date__month=month,
        is_active=True
    ).order_by('date')

    # Create calendar
    cal = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]

    # Previous and next month navigation
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1

    context = {
        'calendar': cal,
        'events': events,
        'month': month,
        'year': year,
        'month_name': month_name,
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
    }
    return render(request, 'dashboard/calendar.html', context)
