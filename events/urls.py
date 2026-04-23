from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'events'

urlpatterns = [
    path('', views.event_list, name='event_list'),
    path('<int:pk>/', views.event_detail, name='event_detail'),
    path('category/<slug:slug>/', views.events_by_category, name='events_by_category'),
    path('search/', views.search_events, name='search_events'),
    path('advanced-search/', views.advanced_search, name='advanced_search'),
    path('favorite/<int:event_id>/', views.toggle_favorite, name='toggle_favorite'),
    path('review/<int:event_id>/', views.add_review, name='add_review'),
    path('book/<int:event_id>/', views.book_event, name='book_event'),
    path('booking/confirmation/<int:booking_id>/', views.booking_confirmation, name='booking_confirmation'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('cancel-booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('create/', views.create_event, name='create_event'),
    path('my-events/', views.my_events, name='my_events'),
    path('edit/<int:event_id>/', views.edit_event, name='edit_event'),
    path('delete/<int:event_id>/', views.delete_event, name='delete_event'),
    path('create-venue/', views.create_venue, name='create_venue'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)