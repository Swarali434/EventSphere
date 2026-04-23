from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import Notification, NotificationPreference


@login_required
def notification_list(request):
    notifications = Notification.objects.filter(user=request.user)

    # Pagination
    paginator = Paginator(notifications, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'unread_count': notifications.filter(is_read=False).count(),
    }
    return render(request, 'notifications/notification_list.html', context)


@login_required
def mark_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})

    return redirect('notifications:notification_list')


@login_required
def mark_all_as_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    messages.success(request, 'All notifications marked as read.')
    return redirect('notifications:notification_list')


@login_required
def notification_preferences(request):
    preferences, created = NotificationPreference.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        preferences.email_notifications = request.POST.get('email_notifications') == 'on'
        preferences.booking_confirmations = request.POST.get('booking_confirmations') == 'on'
        preferences.event_reminders = request.POST.get('event_reminders') == 'on'
        preferences.event_updates = request.POST.get('event_updates') == 'on'
        preferences.marketing_emails = request.POST.get('marketing_emails') == 'on'
        preferences.save()
        messages.success(request, 'Notification preferences updated successfully.')
        return redirect('notifications:notification_preferences')

    context = {
        'preferences': preferences,
    }
    return render(request, 'notifications/notification_preferences.html', context)


def create_notification(user, title, message, notification_type, event=None, booking=None):
    """Helper function to create notifications"""
    Notification.objects.create(
        user=user,
        title=title,
        message=message,
        notification_type=notification_type,
        event=event,
        booking=booking
    )
