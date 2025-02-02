from django.urls import path
from . import views  # Import views from the current app

urlpatterns = [
    path('', views.index, name='home'),  # Route for the home page at "/"
    path('entries/', views.entry_list, name='entry_list'),
    path('workouts', views.workout_selection, name='workout_selection'),
    path('workout/bodyweight', views.body_weight_exercises, name='body_weight_exercises'),
    path('workout/youtube', views.youtube, name='youtube'),

]
