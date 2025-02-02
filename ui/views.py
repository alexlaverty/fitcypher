from collections import defaultdict
from core.models import Entry
from datetime import datetime
from django.contrib.auth.models import User
from django.db.models import Count, Sum
from django.shortcuts import render, redirect
from django.utils import timezone
import logging

# Set up logging
logger = logging.getLogger(__name__)

def index(request):
    # Get the total number of users
    total_users = User.objects.count()

    # Get the total number of entries
    total_entries = Entry.objects.count()

    # Pass the data to the template
    context = {
        'total_users': total_users,
        'total_entries': total_entries,
    }
    return render(request, 'index.html', context)

def entry_list(request):
    if not request.user.is_authenticated:
        return render(request, 'error.html', {'message': 'You must be logged in to view entries.'})

    logger.debug("Starting entry_list view processing")

    # Get all entries for the logged-in user
    entries = Entry.objects.filter(user=request.user).order_by('-date')
    logger.debug(f"Total entries fetched: {entries.count()}")

    # Group entries by day first
    daily_entries = defaultdict(list)
    
    # Get unique days
    unique_days = sorted(set(entry.date.strftime('%Y-%m-%d') for entry in entries), reverse=True)
    logger.debug(f"Unique days found: {len(unique_days)}")

    for day in unique_days:
        logger.debug(f"\nProcessing day: {day}")
        day_entries = entries.filter(date__date=day)
        logger.debug(f"Total entries for day {day}: {day_entries.count()}")
        
        # Handle exercise entries
        exercise_entries = day_entries.filter(tracking='exercise')
        logger.debug(f"Exercise entries found for day {day}: {exercise_entries.count()}")
        
        if exercise_entries.exists():
            logger.debug("Exercise entries exist, processing summaries...")
            
            # Log raw exercise entries for debugging
            for entry in exercise_entries:
                logger.debug(f"Raw exercise entry: name={entry.string_value}, value={entry.numerical_value}")
            
            # Group exercises by name and sum their counts
            exercise_summary = (
                exercise_entries
                .values('string_value')
                .annotate(total_count=Sum('numerical_value'))
                .order_by('string_value')
            )
            
            logger.debug("Exercise summary after grouping:")
            for ex in exercise_summary:
                logger.debug(f"Grouped exercise: {ex['string_value']}, total={ex['total_count']}")
                
                # Create a custom object that mimics Entry model
                summarized_entry = type('SummarizedEntry', (), {
                    'tracking': 'exercise',
                    'string_value': ex['string_value'],
                    'numerical_value': ex['total_count'],
                    'date': exercise_entries.filter(string_value=ex['string_value']).first().date,
                    'tags': None,
                    'notes': None,
                })
                
                logger.debug(f"Adding summarized entry to daily_entries: {summarized_entry.string_value} - {summarized_entry.numerical_value}")
                daily_entries[day].append(summarized_entry)
            
            # Important: Skip adding individual exercise entries since we've summarized them
            non_exercise_entries = day_entries.exclude(tracking='exercise')
            logger.debug(f"Non-exercise entries for day {day}: {non_exercise_entries.count()}")
            daily_entries[day].extend(non_exercise_entries)
            
        else:
            # If no exercise entries, add all entries normally
            logger.debug(f"No exercise entries for day {day}, adding all entries normally")
            daily_entries[day].extend(day_entries)

    # Convert to sorted list of tuples
    grouped_entries = sorted(daily_entries.items(), reverse=True)
    logger.debug(f"\nFinal number of days in grouped_entries: {len(grouped_entries)}")
    
    # Log final structure
    for day, day_entries in grouped_entries:
        logger.debug(f"\nDay {day} has {len(day_entries)} entries:")
        for entry in day_entries:
            logger.debug(f"- {entry.tracking}: {entry.string_value} - {entry.numerical_value}")

    return render(request, 'entry_list.html', {
        'grouped_entries': grouped_entries,
        'debug_mode': True  # Add this to enable template debugging
    })

def workout_selection(request):
    workouts = [
        {
            "title": "Quick Bodyweight Workout",
            "description": "A simple bodyweight workout for a fast and effective session.",
            "view_name": "body_weight_exercises",
            "image_url": "static/workouts/body_weight_workout.jpg"
        },
        {
            "title": "DareBee Workout",
            "description": "Workout to DareBee Youtube Video Library",
            "view_name": "youtube",
            "youtube_channel": "darebee",
            "image_url": "static/workouts/darebee-logo.jpg"
        }
    ]
    return render(request, "workouts.html", {"workouts": workouts})

# List of body weight exercises
BODY_WEIGHT_EXERCISES = [
    "push-ups",
    "pull-ups",
    "squats",
    "lunges",
    "plank",
    "burpees",
    "mountain climbers",
    "jumping jacks",
    "dips",
    "sit-ups",
]

def body_weight_exercises(request):
    if not request.user.is_authenticated:
        return redirect('auth_login')  # Redirect to login if user is not authenticated

    today = timezone.now().date()  # Get today's date

    # Count the number of entries for each exercise for today
    exercise_data = []
    for exercise in BODY_WEIGHT_EXERCISES:
        entry_count = Entry.objects.filter(
            user=request.user,
            tracking="exercise",
            string_value=exercise.lower(),
            date__date=today  # Filter by today's date
        ).count()
        exercise_data.append({
            'name': exercise,
            'entry_count': entry_count,
        })

    # Handle POST request to add an entry
    if request.method == 'POST':
        exercise_name = request.POST.get('exercise_name')
        if exercise_name in BODY_WEIGHT_EXERCISES:
            Entry.objects.create(
                user=request.user,
                date=timezone.now(),
                tracking="exercise",
                string_value=exercise_name.lower(),
                numerical_value=1,
                source="fitcypher"
            )
            return redirect('body_weight_exercises')  # Refresh the page after adding an entry

    return render(request, 'body_weight_exercises.html', {'exercise_data': exercise_data})

def youtube(request):
    youtube_channel = request.GET.get('youtube_channel', '')  # Gets the parameter from URL, empty string as default
    return render(request, 'youtube.html', {'youtube_channel': youtube_channel})