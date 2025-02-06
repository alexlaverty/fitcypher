from django.urls import path, include
from rest_framework import routers
from .views import EntryList, BatchEntryImport, SubmitEntryView, TrackingDataView, EntryViewSet

# Create a router and register your viewsets with it.
router = routers.DefaultRouter()
router.register(r'entries', EntryViewSet)

urlpatterns = [
    path('', include(router.urls)),  # This will include the root API view
    path('entries/list/', EntryList.as_view(), name='api_entries'),
    path('entries/batch/', BatchEntryImport.as_view(), name='api_batch_entries'),
    path('submit/', SubmitEntryView.as_view(), name='api_submit_entry'),
    path('tracking/<str:tracking_type>/', TrackingDataView.as_view(), name='api_get_tracking_data'),
    path('api-auth/', include('rest_framework.urls')),
]