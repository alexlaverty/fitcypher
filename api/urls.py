from django.urls import path, include
from rest_framework import routers
from . import views

# Create a router and register your viewsets with it.
router = routers.DefaultRouter()


urlpatterns = [
    path('', include(router.urls)),  # This will include the root API view
    path('entries/', views.EntryList.as_view(), name='api_entries'),
    path('entries/batch/', views.BatchEntryImport.as_view()),
    path('api-auth/', include('rest_framework.urls')),
    path('submit/', views.api_submit_entry, name='api_submit_entry'),
    path('tracking/<str:tracking_type>/', views.api_get_tracking_data, name='api_get_tracking_data'),
]