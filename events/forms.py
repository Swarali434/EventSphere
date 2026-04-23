from django import forms
from django.db import models
from .models import Category, Event, Venue
from django.utils import timezone


class EventSearchForm(forms.Form):
    PRICE_CHOICES = [
        ('', 'Any Price'),
        ('0-25', '$0 - $25'),
        ('25-50', '$25 - $50'),
        ('50-100', '$50 - $100'),
        ('100-200', '$100 - $200'),
        ('200+', '$200+'),
    ]
    
    DATE_CHOICES = [
        ('', 'Any Date'),
        ('today', 'Today'),
        ('tomorrow', 'Tomorrow'),
        ('this_week', 'This Week'),
        ('this_month', 'This Month'),
        ('next_month', 'Next Month'),
    ]
    
    query = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search events, venues, or locations...'
        })
    )
    
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    price_range = forms.ChoiceField(
        choices=PRICE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    date_range = forms.ChoiceField(
        choices=DATE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    location = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'City or venue...'
        })
    )
    
    def filter_events(self, queryset):
        """Apply filters to the event queryset"""
        if self.cleaned_data.get('query'):
            query = self.cleaned_data['query']
            queryset = queryset.filter(
                models.Q(title__icontains=query) |
                models.Q(description__icontains=query) |
                models.Q(venue__name__icontains=query)
            )
        
        if self.cleaned_data.get('category'):
            queryset = queryset.filter(category=self.cleaned_data['category'])
        
        if self.cleaned_data.get('location'):
            location = self.cleaned_data['location']
            queryset = queryset.filter(
                models.Q(venue__city__icontains=location) |
                models.Q(venue__name__icontains=location)
            )
        
        if self.cleaned_data.get('price_range'):
            price_range = self.cleaned_data['price_range']
            if price_range == '0-25':
                queryset = queryset.filter(price__lte=25)
            elif price_range == '25-50':
                queryset = queryset.filter(price__gte=25, price__lte=50)
            elif price_range == '50-100':
                queryset = queryset.filter(price__gte=50, price__lte=100)
            elif price_range == '100-200':
                queryset = queryset.filter(price__gte=100, price__lte=200)
            elif price_range == '200+':
                queryset = queryset.filter(price__gte=200)
        
        if self.cleaned_data.get('date_range'):
            date_range = self.cleaned_data['date_range']
            now = timezone.now()
            
            if date_range == 'today':
                queryset = queryset.filter(date__date=now.date())
            elif date_range == 'tomorrow':
                tomorrow = now + timezone.timedelta(days=1)
                queryset = queryset.filter(date__date=tomorrow.date())
            elif date_range == 'this_week':
                week_end = now + timezone.timedelta(days=7)
                queryset = queryset.filter(date__gte=now, date__lte=week_end)
            elif date_range == 'this_month':
                month_end = now.replace(day=1) + timezone.timedelta(days=32)
                month_end = month_end.replace(day=1) - timezone.timedelta(days=1)
                queryset = queryset.filter(date__gte=now, date__lte=month_end)
            elif date_range == 'next_month':
                next_month = now.replace(day=1) + timezone.timedelta(days=32)
                next_month = next_month.replace(day=1)
                month_end = next_month + timezone.timedelta(days=32)
                month_end = month_end.replace(day=1) - timezone.timedelta(days=1)
                queryset = queryset.filter(date__gte=next_month, date__lte=month_end)
        
        return queryset


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'category', 'venue', 'date', 'price', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'venue': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date'].input_formats = ['%Y-%m-%dT%H:%M']


class VenueForm(forms.ModelForm):
    class Meta:
        model = Venue
        fields = ['name', 'address', 'city', 'state', 'zip_code', 'capacity']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'zip_code': forms.TextInput(attrs={'class': 'form-control'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control'}),
        }
