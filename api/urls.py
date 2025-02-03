from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()

urlpatterns = [
    path('entries/', views.EntryList.as_view()),
    path('entries/batch/', views.BatchEntryImport.as_view()),
    path('api-auth/', include('rest_framework.urls')),
]