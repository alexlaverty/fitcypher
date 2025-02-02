from core.models import Entry
from collections import defaultdict
from datetime import datetime
from django.db.models import Count
from django.shortcuts import render
from django.shortcuts import render
from django.utils import timezone

def index(request):
    return render(request, 'index.html')  # Render the home page template

def entry_list(request):
    if not request.user.is_authenticated:
        return render(request, 'error.html', {'message': 'You must be logged in to view entries.'})

    # Get all entries for the logged-in user, ordered by date (newest first)
    entries = Entry.objects.filter(user=request.user).order_by('-date')

    # Group entries by day
    grouped_entries = defaultdict(list)
    for entry in entries:
        day = entry.date.strftime('%Y-%m-%d')  # Group by date (without time)
        grouped_entries[day].append(entry)

    # Convert the defaultdict to a list of tuples for easier iteration in the template
    grouped_entries = sorted(grouped_entries.items(), reverse=True)

    return render(request, 'entry_list.html', {'grouped_entries': grouped_entries})