from django.urls import path
from . import views  # Import views from the current app

urlpatterns = [
    path('', views.index, name='home'),  # Route for the home page at "/"
    path('entries/', views.entry_list, name='entry_list'),
    path('entry/chart/', views.entry_charts, name='entry_charts'),
    path('workouts', views.workout_selection, name='workout_selection'),
    path('workout/bodyweight', views.body_weight_exercises, name='body_weight_exercises'),
    path('workout/youtube', views.youtube, name='youtube'),
    path('blood_pressure', views.blood_pressure_view, name='blood_pressure_view'),
    path('weight/', views.weight_tracking_view, name='weight_tracking_view'),
    path('dashboard/<str:tracking_type>/', views.health_dashboard, name='health_dashboard'),
    path('heatmap/', views.heatmap, name='heatmap'),
]


