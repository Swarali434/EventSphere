from django.contrib import admin
from .models import Category, Venue, Event, UserFavorite, Review, Booking, Ticket


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'state', 'capacity']
    list_filter = ['city', 'state']
    search_fields = ['name', 'city']


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'venue', 'date', 'price', 'is_active']
    list_filter = ['category', 'is_active', 'date']
    search_fields = ['title', 'description']
    date_hierarchy = 'date'


@admin.register(UserFavorite)
class UserFavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'event', 'created_at']
    list_filter = ['created_at']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['event', 'user', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']


class TicketInline(admin.TabularInline):
    model = Ticket
    extra = 0
    readonly_fields = ['ticket_number']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['booking_reference', 'user', 'event', 'quantity', 'total_amount', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['booking_reference', 'user__username', 'event__title']
    readonly_fields = ['booking_reference', 'total_amount']
    inlines = [TicketInline]


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['ticket_number', 'booking', 'is_used', 'used_at']
    list_filter = ['is_used', 'used_at']
    search_fields = ['ticket_number', 'booking__booking_reference']
    readonly_fields = ['ticket_number']
