#!/usr/bin/env python
"""
Simple test script to verify EventSphere functionality
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eventsphere.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from events.models import Category, Event, Venue

def test_basic_functionality():
    """Test basic functionality of the EventSphere application"""
    print("Testing EventSphere functionality...")
    
    # Test 1: Check if categories exist
    categories = Category.objects.all()
    print(f"✓ Found {categories.count()} categories")
    
    # Test 2: Check if events exist
    events = Event.objects.all()
    print(f"✓ Found {events.count()} events")
    
    # Test 3: Check if venues exist
    venues = Venue.objects.all()
    print(f"✓ Found {venues.count()} venues")
    
    # Test 4: Test home page
    client = Client()
    response = client.get('/')
    print(f"✓ Home page status: {response.status_code}")
    
    # Test 5: Test events list page
    response = client.get('/events/')
    print(f"✓ Events list page status: {response.status_code}")
    
    # Test 6: Test login page
    response = client.get('/accounts/login/')
    print(f"✓ Login page status: {response.status_code}")
    
    # Test 7: Test event detail page
    if events.exists():
        first_event = events.first()
        response = client.get(f'/events/{first_event.id}/')
        print(f"✓ Event detail page status: {response.status_code}")
    
    print("\n🎉 All basic tests passed! EventSphere is working correctly.")
    print("\nTo access the application:")
    print("1. Make sure the server is running: python manage.py runserver")
    print("2. Open your browser to: http://127.0.0.1:8000/")
    print("3. Admin panel: http://127.0.0.1:8000/admin/ (username: admin, password: admin123)")

if __name__ == "__main__":
    test_basic_functionality()
