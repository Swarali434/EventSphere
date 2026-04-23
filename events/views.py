from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q, Avg
from django.contrib import messages
from django.utils import timezone
from .models import Event, Category, UserFavorite, Review, Booking, Ticket
from .forms import EventSearchForm, EventForm, VenueForm
from django.core.paginator import Paginator


def home(request):
    categories = Category.objects.all()

    # Show latest updated events
    featured_events = Event.objects.filter(is_active=True).order_by('-date')[:6]

    # Category-wise latest events
    concerts = Event.objects.filter(category__slug='concert', is_active=True).order_by('-date')[:3]
    festivals = Event.objects.filter(category__slug='festival', is_active=True).order_by('-date')[:3]
    sports = Event.objects.filter(category__slug='sports', is_active=True).order_by('-date')[:3]

    context = {
        'categories': categories,
        'featured_events': featured_events,
        'concerts': concerts,
        'festivals': festivals,
        'sports': sports,
    }
    return render(request, 'events/home.html', context)


def event_list(request):
    events = Event.objects.filter(is_active=True).order_by('date')
    categories = Category.objects.all()

    # Pagination
    paginator = Paginator(events, 12)  # Show 12 events per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'categories': categories,
    }
    return render(request, 'events/event_list.html', context)


def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk, is_active=True)
    reviews = event.reviews.all().order_by('-created_at')
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']

    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = UserFavorite.objects.filter(user=request.user, event=event).exists()

    context = {
        'event': event,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'is_favorite': is_favorite,
    }
    return render(request, 'events/event_detail.html', context)


def events_by_category(request, slug):
    category = get_object_or_404(Category, slug=slug)
    events = Event.objects.filter(category=category, is_active=True).order_by('date')

    # Pagination
    paginator = Paginator(events, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'category': category,
        'page_obj': page_obj,
    }
    return render(request, 'events/events_by_category.html', context)


def search_events(request):
    form = EventSearchForm(request.GET or None)
    events = Event.objects.filter(is_active=True).order_by('date')

    if form.is_valid():
        events = form.filter_events(events)

    # Pagination
    paginator = Paginator(events, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'form': form,
        'query': request.GET.get('q', ''),
    }
    return render(request, 'events/search_results.html', context)


def advanced_search(request):
    form = EventSearchForm(request.GET or None)
    events = Event.objects.filter(is_active=True).order_by('date')

    if form.is_valid():
        events = form.filter_events(events)

    # Pagination
    paginator = Paginator(events, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'form': form,
    }
    return render(request, 'events/advanced_search.html', context)


@login_required
def toggle_favorite(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    favorite, created = UserFavorite.objects.get_or_create(user=request.user, event=event)

    if not created:
        favorite.delete()
        is_favorite = False
        message = 'Event removed from favorites'
    else:
        is_favorite = True
        message = 'Event added to favorites'

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'is_favorite': is_favorite,
            'message': message
        })

    messages.success(request, message)
    return redirect('events:event_detail', pk=event_id)


@login_required
def add_review(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        if rating and comment:
            review, created = Review.objects.get_or_create(
                event=event,
                user=request.user,
                defaults={'rating': rating, 'comment': comment}
            )

            if not created:
                review.rating = rating
                review.comment = comment
                review.save()
                messages.success(request, 'Your review has been updated!')
            else:
                messages.success(request, 'Your review has been added!')
        else:
            messages.error(request, 'Please provide both rating and comment.')

    return redirect('events:event_detail', pk=event_id)


@login_required
def book_event(request, event_id):
    event = get_object_or_404(Event, id=event_id, is_active=True)

    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))

        # Create booking (Defaults to pending)
        booking = Booking.objects.create(
            user=request.user,
            event=event,
            quantity=quantity,
            total_amount=event.price * quantity
        )

        messages.info(request, f'Please complete the payment for your {quantity} ticket(s).')
        return redirect('events:initiate_payment', booking_id=booking.id)

    context = {
        'event': event,
    }
    return render(request, 'events/book_event.html', context)


@login_required
def booking_confirmation(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    context = {
        'booking': booking,
    }
    return render(request, 'events/booking_confirmation.html', context)


@login_required
def initiate_payment(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    if booking.status != 'pending':
        return redirect('events:booking_confirmation', booking_id=booking.id)

    # UPI Details (Replace with actual VPA for a real app)
    vpa = "upi@okicici" # Placeholder
    name = "EventSphere"
    amount = float(booking.total_amount)
    note = f"Booking {booking.booking_reference}"
    
    # Generate UPI URL
    upi_payload = f"upi://pay?pa={vpa}&pn={name}&am={amount}&tn={note}&cu=INR"
    
    # Use a public QR API for convenience
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&data={upi_payload}"

    context = {
        'booking': booking,
        'upi_payload': upi_payload,
        'qr_url': qr_url,
        'vpa': vpa
    }
    return render(request, 'events/pay_upi.html', context)


@login_required
def confirm_payment(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    if request.method == 'POST':
        transaction_id = request.POST.get('transaction_id')
        if transaction_id:
            booking.transaction_id = transaction_id
            booking.status = 'confirmed'
            booking.save()

            # Create tickets now that it's confirmed
            if not booking.tickets.exists():
                for i in range(booking.quantity):
                    Ticket.objects.create(booking=booking)

            # Create notification
            from notifications.views import create_notification
            create_notification(
                user=request.user,
                title='Booking Confirmed',
                message=f'Your booking for {booking.event.title} has been confirmed. Booking reference: {booking.booking_reference}',
                notification_type='booking_confirmed',
                event=booking.event,
                booking=booking
            )

            # Send confirmation email
            from .email_utils import send_booking_confirmation_email
            send_booking_confirmation_email(booking)

            messages.success(request, 'Payment submitted! Your booking is now confirmed.')
            return redirect('events:booking_confirmation', booking_id=booking.id)
        else:
            messages.error(request, 'Please provide the Transaction ID (UTR).')
    
    return redirect('events:initiate_payment', booking_id=booking.id)


@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user)
    context = {
        'bookings': bookings,
    }
    return render(request, 'events/my_bookings.html', context)


@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    if booking.status == 'confirmed' and booking.event.date > timezone.now():
        booking.status = 'cancelled'
        booking.save()

        # Create notification
        from notifications.views import create_notification
        create_notification(
            user=request.user,
            title='Booking Cancelled',
            message=f'Your booking for {booking.event.title} has been cancelled. Booking reference: {booking.booking_reference}',
            notification_type='booking_cancelled',
            event=booking.event,
            booking=booking
        )

        # Send cancellation email
        from .email_utils import send_booking_cancellation_email
        send_booking_cancellation_email(booking)

        messages.success(request, 'Booking cancelled successfully.')
    else:
        messages.error(request, 'Cannot cancel this booking.')

    return redirect('events:my_bookings')


@login_required
def create_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.is_active = False  # Require admin approval
            event.save()
            messages.success(request, 'Event created successfully! It will be reviewed by our team.')
            return redirect('events:my_events')
    else:
        form = EventForm()

    context = {
        'form': form,
    }
    return render(request, 'events/create_event.html', context)


@login_required
def my_events(request):
    events = Event.objects.filter(created_by=request.user).order_by('-created_at')
    context = {
        'events': events,
    }
    return render(request, 'events/my_events.html', context)


@login_required
def edit_event(request, event_id):
    event = get_object_or_404(Event, id=event_id, created_by=request.user)

    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, 'Event updated successfully!')
            return redirect('events:my_events')
    else:
        form = EventForm(instance=event)

    context = {
        'form': form,
        'event': event,
    }
    return render(request, 'events/edit_event.html', context)


@login_required
def delete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id, created_by=request.user)

    if request.method == 'POST':
        event.delete()
        messages.success(request, 'Event deleted successfully!')
        return redirect('events:my_events')

    context = {
        'event': event,
    }
    return render(request, 'events/delete_event.html', context)


@login_required
def create_venue(request):
    if request.method == 'POST':
        form = VenueForm(request.POST)
        if form.is_valid():
            venue = form.save()
            messages.success(request, f'Venue "{venue.name}" created successfully!')
            return redirect('events:create_event')
    else:
        form = VenueForm()

    context = {
        'form': form,
    }
    return render(request, 'events/create_venue.html', context)
