import json
import logging
import os 
import random
from collections import defaultdict
from core.models import Entry
from datetime import datetime
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count, Sum
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from django.db.models.functions import TruncDate
from django.db.models import Max, Min, Q, Sum, Avg, Count


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
                    'numerical_value': ex['total_count'],  # Convert seconds to minutes
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
        },
        {
            "title": "OPEX Mobility",
            "description": "Workout to OPEX Mobility Youtube Video Library",
            "view_name": "youtube",
            "youtube_channel": "opex-mobility",
            "image_url": "static/workouts/opex-mobility-logo.jpg"
        },
        {
            "title": "OPEX Core",
            "description": "Workout to OPEX Core Youtube Video Library",
            "view_name": "youtube",
            "youtube_channel": "opex-core",
            "image_url": "static/workouts/opex-core-logo.png"
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
                numerical_value=10, # Hard coded to 10 for now...
                tags="quick",
                source="fitcypher"
            )
            return redirect('body_weight_exercises')  # Refresh the page after adding an entry

    return render(request, 'body_weight_exercises.html', {'exercise_data': exercise_data})

@login_required
def youtube(request):
    youtube_channel = request.GET.get('youtube_channel', '')
    
    if request.method == 'POST':
        video_id = request.POST.get('video_id')
        video_title = request.POST.get('video_title')
        video_duration = request.POST.get('video_duration')
        
        # Create entry for completed exercise
        Entry.objects.create(
            user=request.user,
            date=timezone.now(),
            tracking='exercise',
            string_value=video_title,
            numerical_value=video_duration,
            source='youtube',
            tags=youtube_channel,
            notes=f'Video ID: {video_id}'
        )
        return JsonResponse({'status': 'success'})
    
    videos = []
    if youtube_channel:
        APP_DIR = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(APP_DIR, 'data', f'{youtube_channel}.json')
        print(f"json_path: {json_path}")
        if os.path.exists(json_path):
            with open(json_path, 'r') as file:
                videos = json.load(file)
                print("videos")
                print(videos)
                random.shuffle(videos)
        else:
            print(f"Can't find JSON File : {json_path}")
    
    return render(request, 'youtube.html', {
        'youtube_channel': youtube_channel,
        'videos': json.dumps(videos) if videos else '[]'
    })

@login_required
def entry_charts(request):
    # Get the logged-in user's exercise entries
    exercise_entries = Entry.objects.filter(user=request.user, tracking='exercise')

    # Group entries by day and sum the numerical value (converting to minutes)
    daily_data = defaultdict(lambda: defaultdict(float))
    for entry in exercise_entries:
        day = entry.date.strftime('%Y-%m-%d')
        if entry.numerical_value:
            daily_data[day][entry.tags] += float(entry.numerical_value) / 60  # Convert seconds to minutes

    # Prepare the data for the template
    chart_data = {
        'labels': sorted(daily_data.keys()),  # Sorted list of days
        'datasets': []
    }

    # Collect all unique exercise names
    exercise_names = set()
    for day_data in daily_data.values():
        exercise_names.update(day_data.keys())

    # Create a dataset for each exercise
    for exercise in exercise_names:
        dataset = {
            'label': exercise,
            'data': [daily_data[day].get(exercise, 0) for day in chart_data['labels']],
            'backgroundColor': f'rgba({random.randint(0, 255)}, {random.randint(0, 255)}, {random.randint(0, 255)}, 0.6)',
            'borderColor': f'rgba({random.randint(0, 255)}, {random.randint(0, 255)}, {random.randint(0, 255)}, 1)',
            'borderWidth': 1
        }
        chart_data['datasets'].append(dataset)

    return render(request, 'entry_charts.html', {'chart_data': chart_data})


def get_chart_data(user, tracking_type):
    from collections import defaultdict
    from django.utils.timezone import localtime
    import json

    if tracking_type == 'blood_pressure':
        data = defaultdict(lambda: {'systolic': None, 'diastolic': None})
        entries = Entry.objects.filter(user=user, tracking='blood_pressure').order_by('date')

        for entry in entries:
            local_date = localtime(entry.date).strftime('%Y-%m-%d')
            if entry.string_value == 'systolic':
                data[local_date]['systolic'] = float(entry.numerical_value) if entry.numerical_value else None
            elif entry.string_value == 'diastolic':
                data[local_date]['diastolic'] = float(entry.numerical_value) if entry.numerical_value else None

        sorted_dates = sorted(data.keys())
        systolic_values = [data[d]['systolic'] for d in sorted_dates]
        diastolic_values = [data[d]['diastolic'] for d in sorted_dates]

        return json.dumps({
            'labels': sorted_dates,
            'systolic': systolic_values,
            'diastolic': diastolic_values
        })

    else:
        data = {}
        entries = Entry.objects.filter(user=user, tracking=tracking_type).order_by('date')
        for entry in entries:
            local_date = localtime(entry.date).strftime('%Y-%m-%d')
            data[local_date] = float(entry.numerical_value) if entry.numerical_value else None  # Always keeps the latest value

        sorted_dates = sorted(data.keys())
        values = [data[d] for d in sorted_dates]

        return json.dumps({'labels': sorted_dates, 'values': values})

def get_metric_data(user, tracking_type):
    from collections import defaultdict
    from django.utils.timezone import localtime
    import json

    data = defaultdict(list)
    entries = Entry.objects.filter(user=user, tracking=tracking_type).order_by('date')

    for entry in entries:
        local_date = localtime(entry.date).strftime('%Y-%m-%d')
        data['labels'].append(local_date)
        data['values'].append(float(entry.numerical_value) if entry.numerical_value else None)

    return json.dumps(data)


@login_required
def blood_pressure_view(request):
    if request.method == 'POST':
        date = now()
        systolic = request.POST.get('systolic')
        diastolic = request.POST.get('diastolic')

        Entry.objects.create(user=request.user, date=date, tracking='blood_pressure',
                             string_value='systolic', numerical_value=systolic, source='fitcypher')
        Entry.objects.create(user=request.user, date=date, tracking='blood_pressure',
                             string_value='diastolic', numerical_value=diastolic, source='fitcypher')
        return redirect('blood_pressure_view')

    chart_data = get_chart_data(request.user, 'blood_pressure')
    return render(request, 'blood_pressure.html', {'chart_data': chart_data})

def blood_pressure_chart_data(request):
    return JsonResponse(get_chart_data(request.user, 'blood_pressure'), safe=False)

@login_required
def weight_tracking_view(request):
    if request.method == 'POST':
        date = now()
        weight = request.POST.get('weight')
        Entry.objects.create(user=request.user, date=date, tracking='weight',
                             numerical_value=weight, source='fitcypher')
        return redirect('weight_tracking_view')

    chart_data = get_chart_data(request.user, 'weight')
    return render(request, 'weight_tracking.html', {'chart_data': chart_data})

def weight_chart_data(request):
    return JsonResponse(get_chart_data(request.user, 'weight'), safe=False)



# @csrf_exempt
# @login_required
# def api_submit_entry(request):
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             tracking = data.get('tracking')
#             numerical_value = data.get('numerical_value')
#             string_value = data.get('string_value', None)

#             if not tracking or numerical_value is None:
#                 return JsonResponse({'error': 'Tracking and numerical_value are required'}, status=400)

#             Entry.objects.create(
#                 user=request.user,
#                 date=now(),
#                 tracking=tracking,
#                 numerical_value=numerical_value,
#                 string_value=string_value,
#                 source="fitcypher"
#             )

#             return JsonResponse({'message': 'Entry created successfully'}, status=201)

#         except json.JSONDecodeError:
#             return JsonResponse({'error': 'Invalid JSON'}, status=400)

#     return JsonResponse({'error': 'Only POST requests allowed'}, status=405)

# @csrf_exempt
# @login_required
# def api_get_tracking_data(request, tracking_type):
#     from collections import defaultdict
#     from django.utils.timezone import localtime

#     data = defaultdict(list)
#     entries = Entry.objects.filter(user=request.user, tracking=tracking_type).order_by('date')

#     for entry in entries:
#         local_date = localtime(entry.date).strftime('%Y-%m-%d')
#         data['labels'].append(local_date)
#         data['values'].append(float(entry.numerical_value) if entry.numerical_value else None)

#     return JsonResponse(data, safe=False)

@login_required
def health_dashboard(request, tracking_type='weight'):
    chart_data = get_metric_data(request.user, tracking_type)
    return render(request, 'health_dashboard.html', {'chart_data': chart_data, 'tracking_type': tracking_type})


METRIC_COLOR_MAPPING = {
    # 'sleep': {'min': 180, 'max': 540, 'start_color': (255, 0, 0), 'end_color': (0, 255, 0)},
    'weight': {'min': 60, 'max': 80, 'start_color': (255, 0, 0), 'end_color': (0, 255, 0)},
    # 'v02max': {'min': 30, 'max': 50, 'start_color': (255, 0, 0), 'end_color': (0, 255, 0)},
    # 'heart_rate': {'min': 50, 'max': 100, 'start_color': (0, 255, 0), 'end_color': (255, 0, 0)},
    # 'steps': {'min': 2000, 'max': 10000, 'start_color': (255, 0, 0), 'end_color': (0, 255, 0)},
    'exercise_count': {'min': 0, 'max': 50, 'start_color': (255, 0, 0), 'end_color': (0, 255, 0)},
    'exercise_duration': {'min': 0, 'max': 60, 'start_color': (255, 0, 0), 'end_color': (0, 255, 0)},
    # 'fasting_blood_sugar': {'min': 3, 'max': 7, 'start_color': (0, 255, 0), 'end_color': (255, 0, 0)},
    # 'body-bmi': {'min': 18.5, 'max': 24.9, 'start_color': (255, 0, 0), 'end_color': (0, 255, 0)},
    # 'bench_press': {'min': 50, 'max': 200, 'start_color': (255, 0, 0), 'end_color': (0, 255, 0)},
    # 'chins_up': {'min': 0, 'max': 20, 'start_color': (255, 0, 0), 'end_color': (0, 255, 0)},
    # 'cholesterol': {'min': 3, 'max': 7, 'start_color': (0, 255, 0), 'end_color': (255, 0, 0)},
    # 'workout': {'min': 45, 'max': 55, 'start_color': (0, 255, 0), 'end_color': (255, 0, 0)},
}

def calculate_color(value, metric):
    if value is None:
        return '#FFFFFF'  # White for no data

    if metric not in METRIC_COLOR_MAPPING:
        return '#CCCCCC'  # Default gray for unknown metrics

    mapping = METRIC_COLOR_MAPPING[metric]
    min_value = mapping['min']
    max_value = mapping['max']
    start_color = mapping['start_color']
    end_color = mapping['end_color']

    if metric == 'activities-steps' and value > 10000:
        return '#00FF00'  # Green color for steps over 10000

    if metric == 'workout':
        return '#00FF00'  # Green color for workout

    normalized_value = (value - min_value) / (max_value - min_value)
    normalized_value = max(0, min(normalized_value, 1))  # Ensure value is between 0 and 1

    red = int((1 - normalized_value) * start_color[0] + normalized_value * end_color[0])
    green = int((1 - normalized_value) * start_color[1] + normalized_value * end_color[1])
    blue = int((1 - normalized_value) * start_color[2] + normalized_value * end_color[2])

    return f'#{red:02X}{green:02X}{blue:02X}'

def heatmap(request):
    string_values_filter = list(METRIC_COLOR_MAPPING.keys())

    filtered_entries = Entry.objects.filter(user=request.user, string_value__in=string_values_filter)

    heatmap_data = filtered_entries.annotate(truncated_date=TruncDate('date')).values('truncated_date', 'string_value').annotate(avg_numerical_value=Avg('numerical_value'))

    # Filter out entries where numerical_value is null or none for exercise_counts
    exercise_counts = Entry.objects.filter(
        user=request.user,
        tracking='exercise'
    ).exclude(
        string_value__in=['steps', 'heart_rate']
    ).annotate(
        truncated_date=TruncDate('date')
    ).values('truncated_date').annotate(exercise_count=Count('id'))

    # Filter out entries where numerical_value is null or none for exercise_durations
    exercise_durations = Entry.objects.filter(
        user=request.user,
        tracking='exercise'
    ).exclude(
        string_value__in=['steps', 'heart_rate']
    ).exclude(
        numerical_value__isnull=True
    ).annotate(
        truncated_date=TruncDate('date')
    ).values('truncated_date').annotate(exercise_duration=Sum('numerical_value'))

    heatmap_dict = defaultdict(lambda: {string_value: (None, calculate_color(None, string_value)) for string_value in string_values_filter})
    print(heatmap_dict)

    # Add the weight data into the heatmap
    weight_entries = Entry.objects.filter(user=request.user, tracking='weight').annotate(truncated_date=TruncDate('date')).values('truncated_date', 'numerical_value')

    for entry in heatmap_data:
        value = entry['avg_numerical_value']
        metric = entry['string_value']
        color = calculate_color(value, metric)
        if metric == 'sleep':
            value = value / 60
        heatmap_dict[entry['truncated_date']][metric] = (value, color)

    # Process and add weight values to the heatmap
    for weight_entry in weight_entries:
        value = weight_entry['numerical_value']
        date = weight_entry['truncated_date']
        color = calculate_color(value, 'weight')
        heatmap_dict[date]['weight'] = (value, color)

    for count_entry in exercise_counts:
        value = count_entry['exercise_count']
        color = calculate_color(value, 'exercise_count')
        heatmap_dict[count_entry['truncated_date']]['exercise_count'] = (value, color)

    print(exercise_durations)
    for count_entry in exercise_durations:
        value = count_entry['exercise_duration']
        value = value / 60
        color = calculate_color(value, 'exercise_duration')
        heatmap_dict[count_entry['truncated_date']]['exercise_duration'] = (value, color)

    sorted_dates = sorted(heatmap_dict.keys(), reverse=True)

    context = {
        'heatmap_data': {date: heatmap_dict[date] for date in sorted_dates},
        'string_values_filter': string_values_filter,
    }

    return render(request, 'heatmap.html', context)